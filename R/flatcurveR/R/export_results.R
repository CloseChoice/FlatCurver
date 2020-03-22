#' @name export_results
#' @rdname export_results
#' 
#' @title Functions for exporting the results
#' 
#' @description Saves the table containing the restriction effects to a csv file.
#' 
#' @param coefs The data.table containing the restriction effects as returned by the function \code{fit_lme}.
#' @param destination The path to the destination file to which the results sould be written.
#'
#' @return Saves a csv file.
#'
#' @export
export_results <- function (coefs, destination) {
  fwrite(coefs, file = destination, sep = ",", dec = ".", quote = TRUE)
}
