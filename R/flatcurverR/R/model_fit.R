
#' @name fit_lme
#' @rdname model_fit
#' 
#' @title Function for estimatind the effects of restrictions on the (smoothed) lograte of the the number of infections
#' 
#' @description Fits a linear mixed equations model effects and returns the parameter estimations for the resitrictions.
#' 
#' @param data The data table returned from the function \code{add_growth_rates}.
#' @param map_restrictions The mapping table returned by the function \code{generate_map_restrictions}.
#'
#' @details The model adds a random intercept and a random effect for the variable 'day' (days since first infection) per federal state.  In addition, fixed effects for the number of days since the effectuation of each restriction are added.
#'
#' @return The fitted model and the coefficient estimations for the fixed effects are returned as a data.table.
#'
#' @import lme4
#' @export
fit_lme <- function (data, map_restrictions, cutoff_date) {
  # Response variable
  response <- "lograte_smooth2"
  # Variables with random effect
  vars_random <- c("day")
  # Variables with fixed effect (only restrictions are used where at least 5 percent of the values are > 0)
  vars_fixed <- map_restrictions[, restriction_id]
  vars_fixed <- vars_fixed[data[, lapply(.SD, function (x) mean(x > 0)), .SDcols = vars_fixed] > 0.05]
  # Set up model formula
  f <- formula(paste(c(
    response,
    paste(c(
      paste(vars_fixed),
      paste0("(", paste(vars_random, sep = "|bundesland)+"), "|bundesland)")
    ), collapse = "+")
  ), collapse = "~"))
  # Fit model
  mod <- lmer(f, data = data[!is.na(get(response))])
  # Extract and prepare regression coefficients of restrictions
  coefs <- data.frame(summary(mod)$coefficients[-1, c("Estimate", "Std. Error")])
  coefs$restriction_id <- rownames(coefs)
  coefs <- merge(coefs, map_restrictions, by = "restriction_id")
  coefs$restriction_id <- NULL
  coefs <- data.table(coefs)
  setnames(coefs, "Std..Error", "se")
  setnames(coefs, "Estimate", "estimate")
  coefs[, lower := estimate - qnorm(0.975) * se]
  coefs[, upper := estimate + qnorm(0.975) * se]
  coefs <- merge(data.table(restriction = map_restrictions[, restriction]), coefs[, .(restriction, lower, estimate, upper)], on = "restriction", all = TRUE)
  coefs[, cutoff_date := cutoff_date]
  return(list("mod" = mod, "coefs" = coefs))
}
