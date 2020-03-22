path_root <- "/wales/wirvsvirus/FlatCurver"
library("flatcurveR")

# Es werden Daten bis zu (einschliesslich) diesem Tag verwendet
cutoff_date <- as.Date("2020-03-19", tz = "Europe/Berlin")

# Mappingtabelle für Bundeslandnamen zu deren Kürzel
dt_map_bundesland <- read_map_bundesland(file.path(path_root, "/data/corona_measures - BL Resarch Mapping.csv"))
# Infektionszahlen
dt_infections <- read_infections(file.path(path_root, "data/Coronavirus.history.v2.csv"), cutoff_date)
# Grenzschliessungen
dt_border_closures <- read_border_closures(file.path(path_root, "data/corona_measures - Grenzkontrollen.csv"), cutoff_date)
# Massnahmen
dt_restrictions <- read_restrictions(file.path(path_root, "data/corona_measures - Measures_Overview.csv"), dt_border_closures, cutoff_date)

dt <- merge_data(dt_infections, dt_restrictions, dt_border_closures, dt_map_bundesland)

dt_map_restrictions <- generate_map_restrictions(dt_restrictions)

dt <- add_growth_rates(dt)

fit <- fit_lme(dt, dt_map_restrictions, cutoff_date)

fit$coefs

export_results(fit$coefs, file.path(path_root, "R/my_results.csv"))
