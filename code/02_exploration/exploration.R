setwd("/wales/wirvsvirus/FlatCurver")

library("data.table")
library("ggplot2")
#library("googlesheets") # Funktioniert momentan nicht

DT_map_BL <- fread("../corona_measures - BL Resarch Mapping.csv")
DT_map_BL <- DT_map_BL[, .(bundesland, short)]


DT <- fread("data/Coronavirus.history.v2.csv")
DT[, date := as.Date(date, tz = "Europe/Berlin")]
dt <- melt(DT, id.vars = c("date", "parent", "label", "lon", "lat"), variable.name = "status", value.name = "number")
dt[, .N, by = parent]

dtDE <- dt[parent == "Deutschland", -"parent", with = FALSE]
dtDE <- merge(dtDE, DT_map_BL, by.x = "label", by.y = "bundesland", all.x = TRUE)
setnames(dtDE, "short", "bundesland")

# Ebenfalls ist die Gruppe "Repatriierte" wenig interessant.
dtDE <- dtDE[label != "Repatriierte"]


DT_measures <- fread("../corona_measures - Measures_Overview.csv")
DT_measures <- DT_measures[, .(gueltig_ab, gueltig_bis, bundesland, measure = label)]
DT_measures[, gueltig_ab := as.Date(gueltig_ab, tz = "Europe/Berlin")]
DT_measures[, gueltig_bis := as.Date(gueltig_bis, tz = "Europe/Berlin")]
DT_measures[is.na(gueltig_bis), gueltig_bis := DT[, max(date)] + 1]

measures <- lapply(DT_measures[, unique(measure)], function (m) {
  tmp <- DT_measures[measure == m]
  tmp[, measure := as.logical(TRUE)]
  setnames(tmp, "measure", m)
  N <- tmp[, .N, by = bundesland][N > 1]
  if (NROW(N) > 0) {
    # <TODO> In Zukuft muss hier ein Vergleich über den ganzen Zeitraum erfolgen!
    tmp <- tmp[tmp[, .(gueltig_ab = min(gueltig_ab)), by = bundesland], on = c("bundesland", "gueltig_ab")]
  }
  setkey(tmp, bundesland, gueltig_ab, gueltig_bis)
})
names(measures) <- DT_measures[, unique(measure)]

dtDE[, date_helper := date]
setkey(dtDE, bundesland, date, date_helper)

tmp <- dtDE
for (m in names(measures)) {
  n0 <- nrow(tmp)
  cols_initial <- colnames(tmp)
  tmp <- foverlaps(tmp, measures[[m]], by.x = c("bundesland", "date", "date_helper"), by.y = c("bundesland", "gueltig_ab", "gueltig_bis"))
  tmp[is.na(get(m)), c(m) := FALSE]
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


dtDEconfirmed <- dtDE[status == "confirmed"]
#dtDEconfirmed[, rate := (number - shift(number, 1)) / (shift(number, 1) - shift(number, 2))]
dtDEconfirmed[, lograte := (log(number) - shift(log(number), 1)) / (shift(log(number), 1) - shift(log(number), 2))]
dtDEconfirmed[, day := as.numeric(difftime(date, .SD[1, date], units = "days")), by = bundesland]
dtDEconfirmed <- na.omit(dtDEconfirmed)
dtDEconfirmed <- dtDEconfirmed[day > 0]

ggplot(dtDEconfirmed, aes(x = day, y = lograte))+ geom_hline(yintercept = 1, col = "red", lty = 2) + geom_line() + facet_wrap(~ bundesland)


# Wie ist eine theoretische infektionskurve (mit dunkelziffern)
# wie sieht die echte aus
# herausfinden, weclhe maßnahmen welchen effekt hat
  # infektionsrate?
  # verschobene testzeitpunkt?
