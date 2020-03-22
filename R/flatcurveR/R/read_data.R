#' @name read_data
#' @rdname read_data
#' 
#' @title Functions for reading raw data
#' 
#' @description Functions for reading data on infections, border closures and further restrictions.
#' 
#' @param file Path to csv file containing the data.
#' @param cutoff_date The cut-off data at which the effects should be estimated. (infection data and restrictions imposed after this date are not used).
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
#' @rdname read_data
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
#' @rdname read_data
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
#' @rdname read_data
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
  DT <- rbind(DT, border_data[, .(gueltig_ab, gueltig_bis, bundesland, label = "Grenzschlie\u00DFung", restriction_id = DT[, max(restriction_id)] + 1)])
  DT[, restriction_id := paste0("m", restriction_id)]
  # Generate list with one data.table per restriction to be returned
  restriction_ids <- DT[, unique(restriction_id)]
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

