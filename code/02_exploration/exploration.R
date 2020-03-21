setwd("/wales/wirvsvirus/FlatCurver")

library("data.table")
library("ggplot2")
#library("googlesheets") # Funktioniert momentan nicht

# Daten laden

# Mappingtabelle Bundesland zu Kürzel
DT_map_BL <- fread("../corona_measures - BL Resarch Mapping.csv")
DT_map_BL <- DT_map_BL[, .(bundesland, short)]

# Zahl der Infizierten usw.
DT <- fread("data/Coronavirus.history.v2.csv")
DT[, date := as.Date(date, tz = "Europe/Berlin")]
dt <- melt(DT, id.vars = c("date", "parent", "label", "lon", "lat"), variable.name = "status", value.name = "number")
dt[, .N, by = parent]

# Reduziere Daten auf nur Deutschland
dtDE <- dt[parent == "Deutschland", -"parent", with = FALSE]
dtDE <- merge(dtDE, DT_map_BL, by.x = "label", by.y = "bundesland", all.x = TRUE)
setnames(dtDE, "short", "bundesland")

# Die Gruppe "Repatriierte" ist wenig interessant und wird entfernt
dtDE <- dtDE[label != "Repatriierte"]

# Maßnahmentabelle
DT_measures <- fread("../corona_measures - Measures_Overview.csv")
DT_measures <- DT_measures[, .(gueltig_ab, gueltig_bis, bundesland, measure = label)]
DT_measures[, gueltig_ab := as.Date(gueltig_ab, tz = "Europe/Berlin")]
DT_measures[, gueltig_bis := as.Date(gueltig_bis, tz = "Europe/Berlin")]
DT_measures[!is.na(gueltig_ab) & is.na(gueltig_bis), gueltig_bis := DT[, max(date)] + 1]
DT_measures <- DT_measures[!is.na(gueltig_ab) & !is.na(gueltig_bis)]
# Entferne Maßnahmen, die noch nicht in Kraft getreten sind
DT_measures <- DT_measures[gueltig_ab <= dtDE[, max(date)]]



# Daten zu Grenzschließungen
DT_borders <- fread("../corona_measures - Grenzkontrollen.csv")
DT_borders <- DT_borders[, .(gueltig_ab, gueltig_bis, bundesland, nachbarstaat)]
DT_borders[, gueltig_ab := as.Date(gueltig_ab, tz = "Europe/Berlin")]
DT_borders[, gueltig_bis := as.Date(gueltig_bis, tz = "Europe/Berlin")]
DT_borders[!is.na(gueltig_ab) & is.na(gueltig_bis), gueltig_bis := DT[, max(date)] + 1]
DT_borders <- DT_borders[!is.na(gueltig_ab) & !is.na(gueltig_bis)]
# Perspektivisch könne man die Information zu Nachbarstaaten in Verbindung mit den relatien Infektionszahlen dort in Verbindung bringen und für die angrenzenden Bundesländern in Zusammenhang mit den Grenzschließungen verwenden.  Der Einfachheit halber wird jetzt aber nur die binäre Information verwendet, ob Grenzschließungen stattfanden oder nicht.


# Füge die Grenzschließungsdaten zu den Maßnahmen hinzu
DT_measures <- rbind(DT_measures, DT_borders[, .(gueltig_ab, gueltig_bis, bundesland, measure = "grenzschliessung")])



# Füge Maßnahmen zu den Infektionsdaten hinzu
measures <- lapply(DT_measures[, unique(measure)], function (m) {
  tmp <- DT_measures[measure == m]
  tmp[, measure := NULL]
  tmp[, c(m) := gueltig_ab]
  N <- tmp[, .N, by = bundesland][N > 1]
  if (NROW(N) > 0) {
    # <TODO> In Zukuft muss hier ein Vergleich über den ganzen Zeitraum erfolgen!
    tmp <- tmp[tmp[, .(gueltig_ab = min(gueltig_ab)), by = bundesland], on = c("bundesland", "gueltig_ab")]
  }
  setkey(tmp, bundesland, gueltig_ab, gueltig_bis)
  return(unique(tmp))
})
names(measures) <- DT_measures[, unique(measure)]

dtDE[, date_helper := date]
setkey(dtDE, bundesland, date, date_helper)

tmp <- dtDE
for (m in names(measures)) {
  n0 <- nrow(tmp)
  cols_initial <- colnames(tmp)
  tmp <- foverlaps(tmp, measures[[m]], by.x = c("bundesland", "date", "date_helper"), by.y = c("bundesland", "gueltig_ab", "gueltig_bis"))
#  tmp[get(m) == "1970-01-01", c(m) := NA]
  tmp[!is.na(get(m)), tmp := as.numeric(difftime(get("date"), get(m), units = "days")) + 1]
  ranges <- tmp[, .(start = which.min(tmp), end = which.max(tmp)), by = .(bundesland, status)]
  tmp[, i := 1:.N, by = .(bundesland, status)]
  for (B in ranges[, unique(bundesland)]) {
    for (S in ranges[, unique(status)]) {
      tmp[(bundesland == B) & (status == S) & i < ranges[(bundesland == B) & (status == S), start], tmp := 0]
      # <TODO> Das Ende muss auch berücksichtigt werden!
    }
  }
  tmp[is.na(tmp), tmp := 0]
  tmp[, c(m) := NULL]
  setnames(tmp, "tmp", m)
  tmp <- tmp[, c(cols_initial, m), with = FALSE]
  
  if (nrow(tmp) != n0) { print("stop!"); break() }
}
tmp <- tmp[, -"date_helper", with = FALSE]

dtDE <- tmp





setorder(dtDE, bundesland, status, date)

# Wie verlaufen die Kurven?
ggplot(dtDE, aes(x = date, y = number, col = status)) + geom_line() + facet_wrap(~ label, scales = "free_y")

# Das Wachstum sollte und sieht exponenetell aus.  Dann ist das logarithmierte Wachstum linear.
# In Bayern hat es augenscheinlich zwei zeitlich getrennte Ansteckungswellen gegeben.  Der einfachheit halber werden daher im folgenden die Fälle aus der ersten Welle (Webasto) entfernt und die kumulierten Zahlen entsprechend zurückgesetzt.
ggplot(dtDE, aes(x = date, y = number, col = status)) + geom_line() + facet_wrap(~ label, scales = "free_y") + scale_y_continuous(trans = "log")

# Alle Fälle für Bayern vor 2020-02-28 werden entfernt.
dtDE[(bundesland == "BY") & (status == "confirmed"), c(NA, diff(number))]
dtDE[bundesland == "BY"][20:34]
corrections <- dtDE[(bundesland == "BY") & (date == "2020-02-27"), .(bundesland, status, correction = number)]
dtDE <- merge(dtDE, corrections, by = c("bundesland", "status"), all = TRUE)
dtDE[bundesland == "BY", number := number - correction]
dtDE <- dtDE[!((bundesland == "BY") & (date < "2020-02-28"))]
dtDE[, correction := NULL]


# Mit den obigen Bereinigungen scheinen die logarithmierten Wachstumsraten nun annähernd linear zu sein.
ggplot(dtDE, aes(x = date, y = number, col = status)) + geom_line() + facet_wrap(~ label, scales = "free_y") + scale_y_continuous(trans = "log")



# Datensatz für nur Infektionen
dtDEconfirmed <- dtDE[status == "confirmed"]

# Normalisiere Datum auf Tage seit Erstinfektion
dtDEconfirmed[, day := as.numeric(difftime(date, .SD[1, date], units = "days")), by = bundesland]

# Fallzahlen logarithmieren (und glätten)
dtDEconfirmed[, number_log := log(number)]
dtDEconfirmed[, number_log_smooth := predict(loess(number_log ~ day, span = 10 / .N)), by = bundesland]

ggplot(melt(dtDEconfirmed[, .(bundesland, day, number_log, number_log_smooth)], id.vars = c("bundesland", "day")), aes(x = day, y = value, col = variable)) + geom_line() + facet_wrap(~ bundesland)

# Wachstumsraten
dtDEconfirmed[, lograte := (number_log - shift(number_log, 1)) / (shift(number_log, 1) - shift(number_log, 2))]
dtDEconfirmed[, lograte_smooth := (number_log_smooth - shift(number_log_smooth, 1)) / (shift(number_log_smooth, 1) - shift(number_log_smooth, 2))]

dtDEconfirmed <- na.omit(dtDEconfirmed)
dtDEconfirmed <- dtDEconfirmed[day > 1]

# Verlauf der Rate der logarithmierten Fallzahlen (mit Glättung)
ggplot(dtDEconfirmed, aes(x = day, y = lograte_smooth)) + geom_hline(yintercept = 1, col = "red", lty = 2) + geom_line() + facet_wrap(~ bundesland, scales = "free_y") + geom_smooth(method = "loess", n = 10)

# Auch die auf Basis geglätteter Fallzahlen ermittlete Rate wird nun geglättet
dtDEconfirmed[, lograte_smooth2 := predict(loess(lograte_smooth ~ day, span = 10 / .N)), by = bundesland]

ggplot(dtDEconfirmed, aes(x = day, y = lograte_smooth2)) + geom_hline(yintercept = 1, col = "red", lty = 2) + geom_line() + facet_wrap(~ bundesland, scales = "free_y")

# Geglättete Änderungsraten mit Maßnahmen
dt_plot <- copy(dtDEconfirmed)
dt_plot_measures <- merge(DT_measures[, .(gueltig_ab, bundesland, measure)], dtDE[, .(date0 = min(date)), by = bundesland], by = "bundesland")[, .(bundesland, measure, day = as.numeric(difftime(gueltig_ab, date0, units = "days")))]
ggplot(dt_plot, aes(x = day, y = lograte_smooth2)) + geom_hline(yintercept = 1, col = "red", lty = 2) + geom_line() + geom_vline(data = dt_plot_measures, aes(xintercept = day, col = measure)) + facet_wrap(~ bundesland, scales = "free_y")



# Inkubationszeit ist 4-14 Tage.  Anstatt Dummyvariablen für die Maßnahmen zu verwenden wird die Anzahl der Tage seit Einführung der Maßnahme geteilt durch 14, aber nach oben auf 1 beschränkt, verwendet für das OLS-Modell.  Für das GAM wird die Anzahl der Tage seit Einführung verwendet






# Modellierung

# Lineares gemischtes Modell
library("lme4")
response <- "number_log_smooth"
vars_random <- c("1", "day")
vars_fixed <- names(measures)[dtDEconfirmed[, lapply(.SD, function (x) mean(x == FALSE)), .SDcols = names(measures)] < 0.95]
f_lme <- formula(paste(c(
  response,
  paste(c(
    paste(vars_fixed),
    paste0("(", paste(vars_random, sep = "|bundesland)+"), "|bundesland)")
  ), collapse = "+")
), collapse = "~"))
mod_lme <- lmer(f_lme, data = dtDEconfirmed)
summary(mod_lme)

# Füge gefittete Werte zum Datensatz hinzu
dtDEconfirmed[, yhat_lme := fitted(mod_lme)]

dt_plot <- melt(dtDEconfirmed[, .(bundesland, day, rate = number_log_smooth, estimate = yhat_lme)], id.vars = c("bundesland", "day"))
dt_plot_measures <- merge(DT_measures[measure %in% vars_fixed, .(gueltig_ab, bundesland, measure)], dtDE[, .(date0 = min(date)), by = bundesland], by = "bundesland")[, .(bundesland, measure, day = as.numeric(difftime(gueltig_ab, date0, units = "days")))]

p <- ggplot(dt_plot, aes(x = day, y = value, col = variable)) + geom_hline(yintercept = 1, col = "red", lty = 2) + geom_line() + geom_vline(data = dt_plot_measures, aes(xintercept = day, lty = measure)) + facet_wrap(~ bundesland, scales = "free_y")
p
ggsave(filename = "/wales/wirvsvirus/geglaettete_log_rate_mit_schaetzung.png", plot = p, width = 12, height = 8)







