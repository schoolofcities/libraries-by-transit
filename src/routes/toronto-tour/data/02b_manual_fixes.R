# Hand-picked fixes to specific legs of the routed tours.
#
# Reads transit_routes.geojson (from 02_transit_itineraries.R), replaces the legs
# listed below, and writes transit_routes_edited.geojson. The original file is
# left untouched, and other legs aren't re-routed.
#
# LINE_OVERRIDES: use the itinerary whose transit rides are exactly these lines
# (least walking among them), searching the same departures as the main script.
#
# TRANSFER_FIXES: R5 sometimes gets off a stop early and walks to the next
# boarding stop, because both catch the same connecting bus (a tie on arrival
# time). For these, the part of the leg up to the given ride is re-routed to that
# ride's boarding stop directly, where riding on is simply faster, and the rest
# of the leg is kept.
#
# Usage:
#   JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64 Rscript 02b_manual_fixes.R

options(java.parameters = "-Xmx8g")

library(r5r)
library(sf)
library(data.table)

args <- commandArgs(trailingOnly = FALSE)
HERE <- dirname(normalizePath(sub("^--file=", "", args[grep("^--file=", args)])))
IN   <- file.path(HERE, "transit_routes.geojson")
OUT  <- file.path(HERE, "transit_routes_edited.geojson")

TZ  <- "America/Toronto"
DAY <- "2026-10-06"

LINE_OVERRIDES <- list(
  list(route = 1,  leg = 1, lines = c("996", "6")),   # Humberwood -> Albion (Line 6 from Humber College)
  list(route = 6,  leg = 2, lines = c("26")),         # Annette Street -> Junction Triangle
  list(route = 6,  leg = 7, lines = c("509", "1")),   # Fort York -> City Hall (Harbourfront to Union, Line 1 to Queen)
  list(route = 3,  leg = 3, lines = c("935", "52")),  # Black Creek -> Weston (Jane, then Lawrence West)
  list(route = 9,  leg = 7, lines = c("501", "22")),  # Beaches -> Gerrard/Ashdale
  list(route = 10, leg = 8, lines = c("16", "116"))   # Bendale -> Kennedy/Eglinton (Eglinton bus west)
)

TRANSFER_FIXES <- list(
  list(route = 1, leg = 4, board_line = "32")         # stay on the 45 to Eglinton, then the 32
)

net   <- build_network(file.path(HERE, "r5"), verbose = FALSE)
segs  <- st_read(IN, quiet = TRUE)
stops <- fread(file.path(HERE, "tour_stops.csv"))

clock <- function(hm) as.POSIXct(paste(DAY, hm), tz = TZ)

itineraries <- function(orig, dest, depart, shortest = FALSE) {
  it <- detailed_itineraries(
    r5r_network = net, origins = orig, destinations = dest, mode = c("WALK", "TRANSIT"),
    departure_datetime = depart, time_window = 1L, suboptimal_minutes = if (shortest) 0L else 10L,
    max_walk_time = 45, max_trip_duration = 240, shortest_path = shortest,
    drop_geometry = FALSE, progress = FALSE
  )
  if (nrow(it)) it[order(it$option, it$segment), ] else it
}

# Same fix as the main script for bogus transfer-walk geometry.
fix_transfer_walks <- function(it) {
  geom <- st_geometry(it)
  for (i in which(it$mode == "WALK")) {
    if (i == 1 || i == nrow(it)) next
    if (it$distance[i] / (60 * max(it$segment_duration[i], 0.1)) <= 5) next
    a <- tail(st_coordinates(geom[[i - 1]])[, 1:2], 1)
    b <- head(st_coordinates(geom[[i + 1]])[, 1:2], 1)
    geom[[i]] <- st_linestring(rbind(a, b))
    it$distance[i] <- as.numeric(st_length(st_sfc(geom[[i]], crs = 4326)))
  }
  st_geometry(it) <- geom
  it
}

# r5r segments -> rows in the output format, clock times from `start`.
as_rows <- function(it, r, k, from_name, to_name, start) {
  seg_end   <- start + 60 * cumsum(it$wait + it$segment_duration)
  seg_start <- seg_end - 60 * it$segment_duration
  st_sf(
    route = r, leg = k, mode = it$mode, route_short_name = it$route,
    from_library = from_name, to_library = to_name,
    segment_depart = format(seg_start, "%H:%M"), segment_arrive = format(seg_end, "%H:%M"),
    wait_min = round(it$wait, 1), duration_min = round(it$segment_duration, 1),
    distance_m = round(it$distance), geometry = st_geometry(it)
  )
}

leg_info <- function(r, k) {
  tour <- stops[route == r][order(stop)]
  old  <- segs[segs$route == r & segs$leg == k, ]
  old  <- old[order(old$segment), ]
  list(from = tour[k], to = tour[k + 1], old = old, depart = clock(old$segment_depart[1]))
}

replacements <- list()

for (o in LINE_OVERRIDES) {
  L <- leg_info(o$route, o$leg)
  orig <- L$from[, .(id = "o", lat, lon)]
  dest <- L$to[, .(id = "d", lat, lon)]
  best <- NULL
  for (m in 0:20) {
    it <- itineraries(orig, dest, L$depart + 60 * m)
    for (opt in unique(it$option)) {
      x <- it[it$option == opt, ]
      if (!identical(x$route[x$mode != "WALK"], o$lines)) next
      start <- clock(x$departure_time[1])
      cand <- list(it = x, start = start, walk = sum(x$distance[x$mode == "WALK"]),
                   arrive = start + 60 * x$total_duration[1])
      if (is.null(best) || cand$walk < best$walk || (cand$walk == best$walk && cand$arrive < best$arrive)) best <- cand
    }
  }
  if (is.null(best)) stop(sprintf("No itinerary using %s for route %d leg %d",
                                  paste(o$lines, collapse = " > "), o$route, o$leg))
  replacements[[length(replacements) + 1]] <- as_rows(
    fix_transfer_walks(best$it), o$route, o$leg, L$from$branch_name, L$to$branch_name, best$start)
  cat(sprintf("Route %2d leg %d: %s -> %s now %s (%d m walking, arrive %s)\n", o$route, o$leg,
              L$from$branch_name, L$to$branch_name, paste(o$lines, collapse = " > "),
              round(best$walk), format(best$arrive, "%H:%M")))
}

for (f in TRANSFER_FIXES) {
  L <- leg_info(f$route, f$leg)
  ride <- which(L$old$route_short_name == f$board_line)[1]
  board <- st_coordinates(L$old$geometry[ride])[1, ]
  it <- itineraries(L$from[, .(id = "o", lat, lon)], data.table(id = "d", lat = board[["Y"]], lon = board[["X"]]),
                    L$depart, shortest = TRUE)
  head_rows <- as_rows(fix_transfer_walks(it), f$route, f$leg, L$from$branch_name, L$to$branch_name,
                       clock(it$departure_time[1]))
  tail_rows <- L$old[ride:nrow(L$old), names(head_rows)]
  replacements[[length(replacements) + 1]] <- rbind(head_rows, tail_rows)
  cat(sprintf("Route %2d leg %d: %s -> %s now %s, then the original %s onward\n", f$route, f$leg,
              L$from$branch_name, L$to$branch_name,
              paste(ifelse(it$route == "", paste0("walk ", round(it$distance), " m"), it$route), collapse = " > "),
              f$board_line))
}

# ── Splice replacements in and renumber segments ──────────────────────────────

fixed <- rbindlist(lapply(replacements, function(x) as.data.table(x)), fill = TRUE)
keep  <- as.data.table(segs)[!paste(route, leg) %in% unique(paste(fixed$route, fixed$leg))]
out   <- rbindlist(list(keep, fixed), fill = TRUE)
out[, order_in_leg := seq_len(.N), by = .(route, leg)]
out <- out[order(route, leg, order_in_leg)]
out[, leg_segment := seq_len(.N), by = .(route, leg)]
out[, segment := seq_len(.N), by = route]
out[, note := ""]
out[leg_segment == 1, note := paste("start", from_library)]
out[, n_leg := .N, by = .(route, leg)]
out[leg_segment == n_leg, note := trimws(paste(note, "arrive", to_library))]
out[, c("order_in_leg", "n_leg") := NULL]
out <- st_as_sf(out)
out <- out[, c("route", "segment", "leg", "leg_segment", "mode", "route_short_name", "note",
               "from_library", "to_library", "segment_depart", "segment_arrive",
               "wait_min", "duration_min", "distance_m")]

if (file.exists(OUT)) file.remove(OUT)
st_write(out, OUT, driver = "GeoJSON", layer_options = "COORDINATE_PRECISION=6", quiet = TRUE)
cat(sprintf("\nWrote %d segments to %s\n", nrow(out), basename(OUT)))
