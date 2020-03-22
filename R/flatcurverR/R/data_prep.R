


#' @name read_data
#' @rdname data_prep
#' 
#' @title Functions for reading raw data
#' 
#' @description Functions for reading data on infections, border closures and further restrictions.
#' 
#' @param file Path to csv file containing the data.
#' @param cutoff_date The cut-off data at which the effects should be estimated (infection data and restrictions imposed after this date are not used).
#' @param border_data A \code{data.table} containing the border closure data returned by the function \code{read_border_closures}.
#'
#' @details \code{read_map_bundesland} reads data for creating a table for mapping federal state names to their two-letter codes.
#'
#' @return An objet of class \code{data.table}.
#'
#' @import data.table
#' @export
read_map_bundesland <- function (file) {
  # Read data
  DT <- fread(file)
  # Data checks
  COLS <- c("bundesland", "short")
  if (!all(COLS %in% colnames(DT))) stop(paste0("Specified file must contain the following columns: '", paste0(paste(COLS, collapse = "', '"), "'.")))
  return(DT[, .(bundesland, short)])
}


#' @name read_data
#' @rdname data_prep
#' @export
read_infections <- function (file, cutoff_date) {
  # Argument checks
  if (missing(cutoff_date)) cutoff_date <- as.Date(Sys.Date(), tz = "Europe/Berlin")
  # Read data
  DT <- fread(file)
  # Data checks
  COLS <- c("date", "parent", "label", "lon", "lat", "confirmed", "recovered", "deaths")
  if (!all(COLS %in% colnames(DT))) stop(paste0("Specified file must contain the following columns: '", paste0(paste(COLS, collapse = "', '"), "'.")))
  # Prep data
  DT[, date := as.Date(date, tz = "Europe/Berlin")]
  DT <- DT[date <= cutoff_date]
  # Wide to long
  dt <- melt(DT, id.vars = c("date", "parent", "label", "lon", "lat"), variable.name = "status", value.name = "number")
  # Reduce data to Germany
  dt <- dt[parent == "Deutschland", -"parent", with = FALSE]
  # Reduct data to only the number of confirmed infected
  dt <- dt[status == "confirmed",]
  # Remove data not pertaining to federal states
  dt <- dt[label != "Repatriierte"]
  # Check validity of cut-off date
  if (cutoff_date > dt[, max(date)]) stop("Ther are no data available for the specified cut-off date, adjust the cut-off date to the last date for which there are infection data.")
  return(dt)
}


#' @name read_data
#' @rdname data_prep
#' @export
read_border_closures <- function (file, cutoff_date) {
  # Argument checks
  if (missing(cutoff_date)) cutoff_date <- as.Date(Sys.Date(), tz = "Europe/Berlin")
  # Read data
  DT <- fread(file)
  # Data checks
  COLS <- c("gueltig_ab", "gueltig_bis", "bundesland", "nachbarstaat")
  if (!all(COLS %in% colnames(DT))) stop(paste0("Specified file must contain the following columns: '", paste0(paste(COLS, collapse = "', '"), "'.")))
  # Prep data
  DT <- DT[, .(gueltig_ab, gueltig_bis, bundesland, nachbarstaat)]
  DT[gueltig_ab == "", gueltig_ab := NA]
  DT[, gueltig_ab := as.Date(gueltig_ab, tz = "Europe/Berlin")]
  DT[gueltig_bis == "", gueltig_bis := NA]
  DT[, gueltig_bis := as.Date(gueltig_bis, tz = "Europe/Berlin")]
  DT[!is.na(gueltig_ab) & is.na(gueltig_bis), gueltig_bis := cutoff_date + 1]
  DT <- DT[!is.na(gueltig_ab) & !is.na(gueltig_bis)]
  return(DT)
}


#' @name read_data
#' @rdname data_prep
#' @export
read_restrictions <- function (file, border_data, cutoff_date) {
  # Argument checks
  if (missing(cutoff_date)) cutoff_date <- as.Date(Sys.Date(), tz = "Europe/Berlin")
  # Read data
  DT <- fread(file)
  # Data checks
  COLS <- c("gueltig_ab", "gueltig_bis", "bundesland", "category")
  if (!all(COLS %in% colnames(DT))) stop(paste0("Specified file must contain the following columns: '", paste0(paste(COLS, collapse = "', '"), "'.")))
  COLS2 <- c("gueltig_ab", "gueltig_bis", "bundesland")
  if (!all(COLS2 %in% colnames(border_data))) stop(paste0("Specified border closure data must contain the following columns: '", paste0(paste(COLS2, collapse = "', '"), "'.")))
  # Prep data
  DT <- DT[, .(gueltig_ab, gueltig_bis, bundesland, restriction = category)]
  DT[gueltig_ab == "", gueltig_ab := NA]
  DT[, gueltig_ab := as.Date(gueltig_ab, tz = "Europe/Berlin")]
  DT[gueltig_bis == "", gueltig_bis := NA]
  DT[, gueltig_bis := as.Date(gueltig_bis, tz = "Europe/Berlin")]
  DT[!is.na(gueltig_ab) & is.na(gueltig_bis), gueltig_bis := cutoff_date + 1]
  DT <- DT[!is.na(gueltig_ab) & !is.na(gueltig_bis)]
  # Remove restrictions which have not yet come into effect
  DT <- DT[gueltig_ab <= cutoff_date]
  # Prep data
  setnames(DT, "restriction", "label")
  # Contents of column 'label' are not valid column names and we thus add a column with restriction ids ("m1", "m2" etc.)
  DT <- merge(DT, DT[, .(label = sort(unique(label)))][, .(label, restriction_id = 1:.N)], by = "label", all = TRUE)
  # Merge restrictions data and border closure data
  DT <- rbind(DT, border_data[, .(gueltig_ab, gueltig_bis, bundesland, label = "Grenzschließung", restriction_id = DT[, max(restriction_id)] + 1)])
  DT[, restriction_id := paste0("m", restriction_id)]
  # Generate list with one data.table per restriction to be returned
  restriction_ids <- DT[, unique(restriction_id)]
  # Füge Maßnahmen zu den Infektionsdaten hinzu
  restrictions <- lapply(restriction_ids, function (m) {
    # Reduce multiple restrictions pertaining to the same restriction group (label) to one row
    tmp <- DT[restriction_id == m, .(gueltig_ab = min(gueltig_ab), gueltig_bis = max(gueltig_bis), restriction_id = min(restriction_id), label = min(label)), by = bundesland]
    tmp[, restriction_id := NULL]
    tmp[, c(m) := gueltig_ab]
    setkey(tmp, bundesland, gueltig_ab, gueltig_bis)
    return(unique(tmp))
  })
  names(restrictions) <- restriction_ids
  return(restrictions)
}

#' @name generate_map_restrictions
#' @rdname data_prep
#' 
#' @title Functions for generating a mapping table of restriction ids to restriction labels
#' 
#' @description On the basis of the restriction data table returned by \code{read_restrictions} a mapping table of restriction ids to restriction labels is generated.
#' 
#' @param restrictions A data table as returned by the function \code{read_restrictions}.
#'
#' @export
generate_map_restrictions <- function (restrictions) {
  map <- rbindlist(lapply(restrictions, function (x) data.table(restriction_id = colnames(x)[ncol(x)], restriction = x[1, label])))
  setorder(map, restriction_id)
  return(map)
}

#' @name remove_webasto
#' @rdname data_prep
#' 
#' @title Functions for removing infection data pertaining to the company Webasto in Bavaria
#' 
#' @description In Bavaria there appears to habe been two waves of infections and all data pertaining to the first one (associated with the company Webasto) are removed.
#' 
#' @param infections The data table from which to remove data.
#' @param start_wave2 The date of the first infection not associated with Webasto.
#'
#' @details The infection numbers before the date specified in start_wave2 are removed and the remaining are set back accordingly.
remove_webasto <- function (infections, start_wave2 = "2020-02-28") {
  start_wave2 <- as.Date(start_wave2, tz = "Europe/Berlin")
  corrections <- infections[(bundesland == "BY") & (date == (start_wave2 - 1)), .(bundesland, status, correction = number)]
  infections <- merge(infections, corrections, by = c("bundesland", "status"), all = TRUE)
  infections[bundesland == "BY", number := number - correction]
  infections <- infections[!((bundesland == "BY") & (date < start_wave2))]
  infections[, correction := NULL]
  return(infections)
}


add_restriction <- function (infections, restriction) {
  # Save number of rows in infection table in order to track whether the date range merge generates duplicate rows
  n0 <- nrow(infections)
  # Save initial column names of infections table
  cols_initial <- colnames(infections)
  # Add helper data column to infections for date range merge
  infections[, date_helper := date]
  setkey(infections, bundesland, date, date_helper)
  # Merge restriction information by date range to the infections data
  infections <- foverlaps(infections, restriction[, -"label"], by.x = c("bundesland", "date", "date_helper"), by.y = c("bundesland", "gueltig_ab", "gueltig_bis"))
  # Current restriction id
  m <- colnames(restriction)[ncol(restriction)]
  infections[!is.na(get(m)), tmp := as.numeric(difftime(get("date"), get(m), units = "days")) + 1]
  # Restrict variable value of restriction to 14 because the incubation time of COVID-19 approximately 4-14 days is and we expect the restrictions to exhibit a stronger effect the longer it has been in effect, but it's effect should be fully exhausted after day 14
  infections[tmp > 14, tmp := 14]
  ranges <- infections[, .(start = which.min(tmp), end = which.max(tmp)), by = .(bundesland, status)]
  # Add helper index per federal state
  infections[, i := 1:.N, by = .(bundesland, status)]
  for (B in ranges[, unique(bundesland)]) {
    for (S in ranges[, unique(status)]) {
      infections[(bundesland == B) & (status == S) & i < ranges[(bundesland == B) & (status == S), start], tmp := 0]
      # <TODO> Das Ende muss auch berücksichtigt werden!
    }
  }
  # Set variable values to zero before restriction came into effect
  infections[is.na(tmp), tmp := 0]
  # Prep data
  infections[, c(m) := NULL]
  setnames(infections, "tmp", m)
  # Remove excess columns
  infections <- infections[, c(cols_initial, m), with = FALSE]
  # Check if number of rows is the same as initially
  if (nrow(infections) != n0) stop("Additional rows were created when adding restriction information to infection data.")
  return(infections)
}


#' @name merge_data
#' @rdname data_prep
#' 
#' @title Function for merging infection and restriction data
#' 
#' @description Function for merging infection and restriction data on the basis of the return values of the functions \code{read_infections}, \code{read_restrictions}, \code{read_border_closures} and \code{read_map_bundesland}.
#' 
#' @param infections Return value from function \code{read_infections}.
#' @param restrictions Return value from function \code{read_restrictions}.
#' @param border_closures Return value from function \code{read_border_closures}.
#' @param map Return value from function \code{read_map_bundesland}.
#'
#' @export
merge_data <- function (infections, restrictions, border_closures, map) {
  # Add federal state mapping to infections
  dt <- merge(infections, map, by.x = "label", by.y = "bundesland", all.x = TRUE)
  setnames(dt, "short", "bundesland")
  # Remove infection cases associated with the company Webasto in Bavaria
  dt <- remove_webasto(dt)
  # Merge restriction information to infections data
  for (m in names(restrictions)) {
    dt <- add_restriction(dt, restrictions[[m]])
  }
  setorder(dt, bundesland, status, date)
  # Normalise date to days since first confirmed infection (starting at 1)
  dt[, day := as.numeric(difftime(date, .SD[1, date], units = "days")), by = bundesland]
  return(dt)
}

#' @name add_growth_rates
#' @rdname data_prep
#' 
#' @title Function to calculate different growth rates
#' 
#' @description Function to calculate different growth rates of the number of infections and add these to the main data set.
#' 
#' @param infections The data table to which the growth rates should be added.
#'
#' @details <TODO> The different growth rates should be described here.
#'
#' @export
add_growth_rates <- function (infections) {
  # Take logarithm of case numbers and smooth values
  infections[, number_log := log(number)]
  infections[, number_log_smooth := predict(loess(number_log ~ day, span = 10 / .N)), by = bundesland]
  # Calculate change rate of raw log numbers
  infections[, lograte := (number_log - shift(number_log, 1)) / (shift(number_log, 1) - shift(number_log, 2)), by = bundesland]
  # Calculate change rate of smoothed log numbers and smooth these as well
  infections[, lograte_smooth := (number_log_smooth - shift(number_log_smooth, 1)) / (shift(number_log_smooth, 1) - shift(number_log_smooth, 2)), by = bundesland]
  infections[!is.na(lograte_smooth), lograte_smooth2 := predict(loess(lograte_smooth ~ day, span = 10 / .N)), by = bundesland]
  return(infections)
}


