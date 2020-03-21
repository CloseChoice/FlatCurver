setwd("/wales/wirvsvirus/FlatCurver")

library("data.table")
library("ggplot2")

DT <- fread("data/Coronavirus.history.v2.csv")
DT[, date := as.Date(date, tz = "Europe/Berlin")]

dt <- melt(DT, id.vars = c("date", "parent", "label", "lon", "lat"), variable.name = "status", value.name = "number")

dt[, .N, by = parent]

dtDE <- dt[parent == "Deutschland", -"parent", with = FALSE]

# Wie verlaufen die Kurven?
ggplot(dtDE, aes(x = date, y = number, col = status)) + geom_line() + facet_wrap(~ label, scales = "free_y")

# Das Wachstum sollte und sieht exponenetell aus.  Dann ist das logarithmierte Wachstum linear.
# In Bayern hat es augenscheinlich zwei zeitlich getrennte Ansteckungswellen gegeben.  Der einfachheit halber werden daher im folgenden die Fälle aus der ersten Welle (Webasto) entfernt und die kumulierten Zahlen entsprechend zurückgesetzt.
ggplot(dtDE, aes(x = date, y = number, col = status)) + geom_line() + facet_wrap(~ label, scales = "free_y") + scale_y_continuous(trans = "log")

# Alle Fälle f Bayern vor 2020-02-28 werden entfernt.
dtDE[(label == "Bayern") & (status == "confirmed"), c(NA, diff(number))]
dtDE[label == "Bayern"][20:34]
dtDE[label == "Bayern"] <- dtDE[dtDE[(label == "Bayern") & (date == "2020-02-27"), .(label, status, correction = number)], on = c("label", "status")]
dtDE[label == "Bayern", number := number - correction]
dtDE <- dtDE[!((label == "Bayern") & (date < "2020-02-28"))]
dtDE[, correction := NULL]

# Ebenfalls ist die Gruppe "Repatriierte" wenig interessant.
dtDE <- dtDE[label != "Repatriierte"]

# Mit den obigen Bereinigungen scheinen die logarithmierten Wachstumsraten nun annähernd linear zu sein.
ggplot(dtDE, aes(x = date, y = number, col = status)) + geom_line() + facet_wrap(~ label, scales = "free_y") + scale_y_continuous(trans = "log")






# Wie ist eine theoretische infektionskurve (mit dunkelziffern)
# wie sieht die echte aus
# herausfinden, weclhe maßnahmen welchen effekt hat
  # infektionsrate?
  # verschobene testzeitpunkt?
