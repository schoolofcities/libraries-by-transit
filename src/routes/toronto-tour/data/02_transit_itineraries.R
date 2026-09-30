# Transit itineraries for the 10 library tours.
#
# For each tour, routes stop 1 -> 2 -> ... -> 10 by walking + TTC transit using
# r5r::detailed_itineraries(), choosing the least-walking itinerary rather than the
# fastest (see least_walking_itinerary()). The tour is at stop 1 at 09:00 on a
# Tuesday; each following leg can leave once the previous leg arrives plus
# DWELL_MIN at the library (later, if leaving later means less walking).
#
# Inputs:
#   tour_stops.csv          (from 01_match_tour_stops.py)
#   r5/toronto.osm.pbf      (OSM clip copied from the transit-oriented-stadiums project)
#   r5/ttc_gtfs.zip         (TTC Routes and Schedules, Toronto Open Data)
#
# Output:
#   transit_routes.geojson  one LineString per itinerary segment (walk or transit),
#                           ordered by route then segment
#
# Usage:
#   Rscript 02_transit_itineraries.R
#
# If rJava can't find libjvm.so, run `sudo R CMD javareconf` once, or prefix the
# command with JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64.
#
# r5r caches the network as r5/network.dat; delete it to rebuild after changing
# the OSM or GTFS inputs.

# ── Config ────────────────────────────────────────────────────────────────────
# java.parameters must be set before r5r loads the JVM.

options(java.parameters = "-Xmx8g")

library(r5r)
library(sf)
library(data.table)

args   <- commandArgs(trailingOnly = FALSE)
HERE   <- dirname(normalizePath(sub("^--file=", "", args[grep("^--file=", args)])))
R5_DIR <- file.path(HERE, "r5")
STOPS  <- file.path(HERE, "tour_stops.csv")
OUT    <- file.path(HERE, "transit_routes.geojson")

TZ        <- "America/Toronto"
START     <- as.POSIXct("2026-10-06 09:00:00", tz = TZ)  # a Tuesday
DWELL_MIN <- 20

# ── Network ───────────────────────────────────────────────────────────────────

net <- build_network(R5_DIR, verbose = FALSE)

# ── Least-walking itinerary for one leg ──────────────────────────────────────
# R5 only minimizes arrival time, so among equally fast trips it will happily walk
# past the nearest stop to catch the same bus one stop earlier. We prefer less
# walking: gather candidates by leaving the library 0..LATER_MIN minutes later
# (which rules out those "walk up the line" ties) and by asking R5 for slower
# alternatives (suboptimal_minutes). Then pick the lowest score, where
# score = walk metres + TRANSFER_PENALTY_M per extra boarding, among candidates
# arriving within ARRIVE_TOL_MIN of the fastest. Ties go to the earliest arrival,
# then the latest start (less waiting at the stop).

LATER_MIN          <- 20
ARRIVE_TOL_MIN     <- 10
TRANSFER_PENALTY_M <- 300

least_walking_itinerary <- function(from, to, depart) {
  cands <- list()
  for (m in 0:LATER_MIN) {
    it <- detailed_itineraries(
      r5r_network        = net,
      origins            = from[, .(id, lat, lon)],
      destinations       = to[, .(id, lat, lon)],
      mode               = c("WALK", "TRANSIT"),
      departure_datetime = depart + 60 * m,
      time_window        = 1L,
      suboptimal_minutes = ARRIVE_TOL_MIN,
      max_walk_time      = 45,
      max_trip_duration  = 240,
      shortest_path      = FALSE,
      drop_geometry      = FALSE,
      progress           = FALSE
    )
    if (nrow(it) == 0) next
    for (o in unique(it$option)) {
      x <- it[it$option == o, ]
      cands[[length(cands) + 1]] <- x[order(x$segment), ]
    }
  }
  if (length(cands) == 0) return(NULL)

  day   <- as.Date(depart, tz = TZ)
  start <- sapply(cands, function(x) as.numeric(as.POSIXct(paste(day, x$departure_time[1]), tz = TZ)))
  arr   <- start + 60 * sapply(cands, function(x) x$total_duration[1])
  walk  <- sapply(cands, function(x) sum(x$distance[x$mode == "WALK"]))
  rides <- sapply(cands, function(x) sum(x$mode != "WALK"))
  score <- walk + TRANSFER_PENALTY_M * pmax(rides - 1, 0)

  ok   <- which(arr <= min(arr) + 60 * ARRIVE_TOL_MIN)
  best <- ok[order(score[ok], arr[ok], -start[ok])][1]
  cands[[best]]
}

# ── Route each tour, chaining departure times leg to leg ─────────────────────

stops <- fread(STOPS)
stops[, id := sprintf("r%02d_s%02d", route, stop)]

legs <- list()

for (r in sort(unique(stops$route))) {
  tour   <- stops[route == r][order(stop)]
  depart <- START

  for (k in seq_len(nrow(tour) - 1)) {
    from <- tour[k]
    to   <- tour[k + 1]

    it <- least_walking_itinerary(from, to, depart)

    if (is.null(it)) stop(sprintf("No itinerary for route %d leg %d (%s -> %s)",
                                  r, k, from$branch_name, to$branch_name))

    # R5 occasionally returns a bogus street path for a transfer walk between two
    # transit segments (e.g. ~1 km drawn for a 1-minute transfer). Replace those
    # with a straight line from the previous segment's end to the next one's start.
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

    # r5r may shift the start slightly within the time window; total_duration and
    # segment waits/durations are counted from its departure_time. Each segment's
    # wait happens before it (e.g. waiting at the stop before boarding a bus).
    leg_start <- as.POSIXct(paste(as.Date(depart, tz = TZ), it$departure_time[1]), tz = TZ)
    seg_end   <- leg_start + 60 * cumsum(it$wait + it$segment_duration)
    seg_start <- seg_end - 60 * it$segment_duration
    arrive    <- leg_start + 60 * it$total_duration[1]

    n <- nrow(it)
    note <- rep("", n)
    note[1] <- paste("start", from$branch_name)
    note[n] <- trimws(paste(note[n], "arrive", to$branch_name))

    legs[[length(legs) + 1]] <- st_sf(
      route            = r,
      leg              = k,
      leg_segment      = it$segment,
      mode             = it$mode,
      route_short_name = it$route,
      note             = note,
      from_library     = from$branch_name,
      to_library       = to$branch_name,
      segment_depart   = format(seg_start, "%H:%M"),
      segment_arrive   = format(seg_end, "%H:%M"),
      wait_min         = round(it$wait, 1),
      duration_min     = round(it$segment_duration, 1),
      distance_m       = round(it$distance),
      geometry         = st_geometry(it)
    )

    cat(sprintf("Route %2d leg %d: %-28s -> %-28s %s-%s  %3d min  %s\n",
                r, k, from$branch_name, to$branch_name, format(leg_start, "%H:%M"),
                format(arrive, "%H:%M"), round(it$total_duration[1]),
                paste(ifelse(it$route == "", it$mode, it$route), collapse = " > ")))

    depart <- arrive + 60 * DWELL_MIN
  }
}

# ── Write ─────────────────────────────────────────────────────────────────────

out <- do.call(rbind, legs)
out$segment <- ave(seq_len(nrow(out)), out$route, FUN = seq_along)
out <- out[, c("route", "segment", setdiff(names(out), c("route", "segment")))]

if (file.exists(OUT)) file.remove(OUT)
st_write(out, OUT, driver = "GeoJSON", layer_options = "COORDINATE_PRECISION=6", quiet = TRUE)
cat(sprintf("\nWrote %d segments across %d routes to %s\n",
            nrow(out), length(unique(out$route)), basename(OUT)))
