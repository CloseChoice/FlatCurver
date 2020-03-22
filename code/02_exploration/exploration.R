setwd("/wales/wirvsvirus/FlatCurver")

update_date <- Sys.Date()#"2020-03-19"

# Die folgende Zeile und die am Ende des Skripts auskommentierten Zeilen werden verwendet, um Schätzwerte für mehrere Stichtage zu generieren (für die Visualisierung)
#####
##########
#    coefs <- lapply(as.Date("2020-03-10", tz = "Europe/Berlin") + 5:9, function (update_date) {
##########
#####


library("data.table")
library("ggplot2")
#library("googlesheets") # Funktioniert momentan nicht

# Daten laden

# Mappingtabelle Bundesland zu Kürzel
DT_map_BL <- fread("data/corona_measures - BL Resarch Mapping.csv")
DT_map_BL <- DT_map_BL[, .(bundesland, short)]

# Zahl der Infizierten usw.
DT <- fread("data/Coronavirus.history.v2.csv")
DT[, date := as.Date(date, tz = "Europe/Berlin")]

DT <- DT[date <= as.Date(update_date)] 

dt <- melt(DT, id.vars = c("date", "parent", "label", "lon", "lat"), variable.name = "status", value.name = "number")
dt[, .N, by = parent]

# Reduziere Daten auf nur Deutschland
dtDE <- dt[parent == "Deutschland", -"parent", with = FALSE]
dtDE <- merge(dtDE, DT_map_BL, by.x = "label", by.y = "bundesland", all.x = TRUE)
setnames(dtDE, "short", "bundesland")

# Die Gruppe "Repatriierte" ist wenig interessant und wird entfernt
dtDE <- dtDE[label != "Repatriierte"]

# Maßnahmentabelle
DT_measures <- fread("data/corona_measures - Measures_Overview.csv")
#DT_measures <- DT_measures[, .(gueltig_ab, gueltig_bis, bundesland, measure = label)]
DT_measures <- DT_measures[, .(gueltig_ab, gueltig_bis, bundesland, measure = category)]
DT_measures[, gueltig_ab := as.Date(gueltig_ab, tz = "Europe/Berlin")]
DT_measures[gueltig_bis == "", gueltig_bis := NA]
DT_measures[, gueltig_bis := as.Date(gueltig_bis, tz = "Europe/Berlin")]
DT_measures[!is.na(gueltig_ab) & is.na(gueltig_bis), gueltig_bis := DT[, max(date)] + 1]
DT_measures <- DT_measures[!is.na(gueltig_ab) & !is.na(gueltig_bis)]
# Entferne Maßnahmen, die noch nicht in Kraft getreten sind
DT_measures <- DT_measures[gueltig_ab <= dtDE[, max(date)]]
setnames(DT_measures, "measure", "label")
DT_measures <- merge(DT_measures, DT_measures[, .(label = sort(unique(label)))][, .(label, measure_id = 1:.N)], by = "label", all = TRUE)




# Daten zu Grenzschließungen
DT_borders <- fread("data/corona_measures - Grenzkontrollen.csv")
DT_borders <- DT_borders[, .(gueltig_ab, gueltig_bis, bundesland, nachbarstaat)]
DT_borders[, gueltig_ab := as.Date(gueltig_ab, tz = "Europe/Berlin")]
DT_borders[, gueltig_bis := as.Date(gueltig_bis, tz = "Europe/Berlin")]
DT_borders[!is.na(gueltig_ab) & is.na(gueltig_bis), gueltig_bis := DT[, max(date)] + 1]
DT_borders <- DT_borders[!is.na(gueltig_ab) & !is.na(gueltig_bis)]
# Perspektivisch könne man die Information zu Nachbarstaaten in Verbindung mit den relatien Infektionszahlen dort in Verbindung bringen und für die angrenzenden Bundesländern in Zusammenhang mit den Grenzschließungen verwenden.  Der Einfachheit halber wird jetzt aber nur die binäre Information verwendet, ob Grenzschließungen stattfanden oder nicht.


# Füge die Grenzschließungsdaten zu den Maßnahmen hinzu
#DT_measures <- rbind(DT_measures, DT_borders[, .(gueltig_ab, gueltig_bis, bundesland, measure = "grenzschliessung")])
DT_measures <- rbind(DT_measures, DT_borders[, .(gueltig_ab, gueltig_bis, bundesland, label = "Grenzschließung", measure_id = DT_measures[, max(measure_id)] + 1)])
DT_measures[, measure_id := paste0("m", measure_id)]


# Füge Maßnahmen zu den Infektionsdaten hinzu
measures <- lapply(DT_measures[, unique(measure_id)], function (m) {
  tmp <- DT_measures[measure_id == m, -"label"]
  tmp <- tmp[, .(gueltig_ab = min(gueltig_ab), gueltig_bis = max(gueltig_bis), measure_id = min(measure_id)), by = bundesland]
  tmp[, measure_id := NULL]
  tmp[, c(m) := gueltig_ab]
  N <- tmp[, .N, by = bundesland][N > 1]
  if (NROW(N) > 0) {
    # <TODO> In Zukuft muss hier ein Vergleich über den ganzen Zeitraum erfolgen!
    tmp <- tmp[tmp[, .(gueltig_ab = min(gueltig_ab)), by = bundesland], on = c("bundesland", "gueltig_ab")]
  }
  setkey(tmp, bundesland, gueltig_ab, gueltig_bis)
  return(unique(tmp))
})
names(measures) <- DT_measures[, unique(measure_id)]

dtDE[, date_helper := date]
setkey(dtDE, bundesland, date, date_helper)






tmp <- dtDE
for (m in names(measures)) {
  n0 <- nrow(tmp)
  cols_initial <- colnames(tmp)
  tmp <- foverlaps(tmp, measures[[m]], by.x = c("bundesland", "date", "date_helper"), by.y = c("bundesland", "gueltig_ab", "gueltig_bis"))
#  tmp[get(m) == "1970-01-01", c(m) := NA]
  tmp[!is.na(get(m)), tmp := as.numeric(difftime(get("date"), get(m), units = "days")) + 1]
  tmp[tmp > 14, tmp := 14]
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
dtDEconfirmed[, lograte := (number_log - shift(number_log, 1)) / (shift(number_log, 1) - shift(number_log, 2)), by = bundesland]
dtDEconfirmed[, lograte_smooth := (number_log_smooth - shift(number_log_smooth, 1)) / (shift(number_log_smooth, 1) - shift(number_log_smooth, 2)), by = bundesland]

# Verlauf der Rate der logarithmierten Fallzahlen (mit Glättung)
ggplot(dtDEconfirmed, aes(x = day, y = lograte_smooth)) + geom_hline(yintercept = 1, col = "red", lty = 2) + geom_line() + facet_wrap(~ bundesland, scales = "free_y") + geom_smooth(method = "loess", n = 10)

# Auch die auf Basis geglätteter Fallzahlen ermittlete Rate wird nun geglättet
dtDEconfirmed[!is.na(lograte_smooth), lograte_smooth2 := predict(loess(lograte_smooth ~ day, span = 10 / .N)), by = bundesland]

ggplot(dtDEconfirmed, aes(x = day, y = lograte_smooth2)) + geom_hline(yintercept = 1, col = "red", lty = 2) + geom_line() + facet_wrap(~ bundesland, scales = "free_y")

# Geglättete Änderungsraten mit Maßnahmen
dt_plot <- copy(dtDEconfirmed)
dt_plot_measures <- merge(DT_measures[, .(gueltig_ab, bundesland, measure_id, label)], dtDE[, .(date0 = min(date)), by = bundesland], by = "bundesland")[, .(bundesland, measure = label, day = as.numeric(difftime(gueltig_ab, date0, units = "days")))]
ggplot(dt_plot, aes(x = day, y = lograte_smooth2)) + geom_hline(yintercept = 1, col = "red", lty = 2) + geom_line() + geom_vline(data = dt_plot_measures, aes(xintercept = day, col = measure)) + facet_wrap(~ bundesland, scales = "free_y")



#dtDEconfirmedNA <- copy(dtDEconfirmed[is.na(lograte_smooth2)])
#dtDEconfirmed <- na.omit(dtDEconfirmed)
#dtDEconfirmed <- dtDEconfirmed[day > 1]




# Modellierung

# Lineares gemischtes Modell
library("lme4")
response <- "number_log_smooth"
vars_random <- c("day")
vars_fixed <- names(measures)[dtDEconfirmed[, lapply(.SD, function (x) mean(x == FALSE)), .SDcols = names(measures)] < 0.95]
f_lme <- formula(paste(c(
  response,
  paste(c(
    paste(vars_fixed),
    paste0("(", paste(vars_random, sep = "|bundesland)+"), "|bundesland)")
  ), collapse = "+")
), collapse = "~"))
mod_lme <- lmer(f_lme, data = dtDEconfirmed[!is.na(number_log_smooth)])
summary(mod_lme)
# Bis auf die Maßnahmen schutz_gef_personen und pandemieplan ist der Effekt wie erwünscht negativ, die Paramter sind allerdings nicht alle signifikant verschieden von Null

# Füge gefittete Werte zum Datensatz hinzu
dtDEconfirmed[!is.na(number_log_smooth), yhat_lme := fitted(mod_lme)]

dt_plot <- melt(dtDEconfirmed[, .(bundesland, day, number_log_smooth, estimate = yhat_lme)], id.vars = c("bundesland", "day"))
dt_plot_measures <- merge(DT_measures[measure_id %in% vars_fixed, .(gueltig_ab, bundesland, label)], dtDE[, .(date0 = min(date)), by = bundesland], by = "bundesland")[, .(bundesland, measure = label, day = as.numeric(difftime(gueltig_ab, date0, units = "days")))]

p <- ggplot(dt_plot, aes(x = day, y = value, col = variable)) + geom_hline(yintercept = 1, col = "red", lty = 2) + geom_line() + geom_vline(data = dt_plot_measures, aes(xintercept = day, lty = measure)) + facet_wrap(~ bundesland, scales = "free_y")
p
#ggsave(filename = "/wales/wirvsvirus/geglaettete_log_rate_mit_schaetzung.png", plot = p, width = 12, height = 8)


## Da die Daten Zeitreihen sind sind die Beobachtungen natürich nicht i.i.d.
#layout(matrix(1:dtDEconfirmed[, uniqueN(bundesland)], nrow = 4))
#lapply(dtDEconfirmed[, unique(bundesland)], function (x) acf(dtDEconfirmed[bundesland == x, number_log_smooth], main = x))

## Berücksichtigung der Korrelationsstruktur der Zeitreihen durch Modellierung mit nlme::lme funktioniert nicht da s nicht konvergiert.  Stattdessen wird mit Differenzierung gearbeitet
#dtDEconfirmed[, number_log_smooth_diff := number_log_smooth - shift(number_log_smooth), by = bundesland]

## Autokorrelation ist noch vorhanden... Sollte vielleicht zweite Differenzen nehmen
#layout(matrix(1:dtDEconfirmed[, uniqueN(bundesland)], nrow = 4))
#lapply(dtDEconfirmed[, unique(bundesland)], function (x) acf(dtDEconfirmed[bundesland == x, number_log_smooth_diff], na.action = na.omit, main = x))

#f_lme_diff <- as.character(f_lme)
#f_lme_diff[2] <- "number_log_smooth_diff"
#f_lme_diff <- formula(paste(f_lme_diff[c(2, 1, 3)], collapse = ""))
#mod_lme_diff <- lmer(f_lme_diff, data = dtDEconfirmed)
#summary(mod_lme_diff)

## Füge gefittete Werte zum Datensatz hinzu
#dtDEconfirmed[!is.na(number_log_smooth_diff), yhat_lme_diff := fitted(mod_lme_diff)]
#dt_plot <- melt(dtDEconfirmed[, .(bundesland, day, number_log_smooth_diff, estimate = yhat_lme_diff)], id.vars = c("bundesland", "day"))

#p <- ggplot(dt_plot, aes(x = day, y = value, col = variable)) + geom_hline(yintercept = 1, col = "red", lty = 2) + geom_line() + geom_vline(data = dt_plot_measures, aes(xintercept = day, lty = measure)) + facet_wrap(~ bundesland, scales = "free_y")
#p



## Versuch mit Differenzen zweiten Grades
#dtDEconfirmed[, number_log_smooth_diff2 := number_log_smooth_diff - shift(number_log_smooth_diff), by = bundesland]

## Autokorrelation ist noch vorhanden... Sollte vielleicht zweite Differenzen nehmen
#layout(matrix(1:dtDEconfirmed[, uniqueN(bundesland)], nrow = 4))
#lapply(dtDEconfirmed[, unique(bundesland)], function (x) acf(dtDEconfirmed[bundesland == x, number_log_smooth_diff2], na.action = na.omit, main = x))

#f_lme_diff2 <- as.character(f_lme)
#f_lme_diff2[2] <- "number_log_smooth_diff2"
#f_lme_diff2 <- formula(paste(f_lme_diff2[c(2, 1, 3)], collapse = ""))
#mod_lme_diff2 <- lmer(f_lme_diff2, data = dtDEconfirmed)
#summary(mod_lme_diff2)

## Füge gefittete Werte zum Datensatz hinzu
#dtDEconfirmed[!is.na(number_log_smooth_diff2), yhat_lme_diff2 := fitted(mod_lme_diff2)]
#dt_plot <- melt(dtDEconfirmed[, .(bundesland, day, rate = number_log_smooth_diff2, estimate = yhat_lme_diff2)], id.vars = c("bundesland", "day"))

#p <- ggplot(dt_plot, aes(x = day, y = value, col = variable)) + geom_hline(yintercept = 1, col = "red", lty = 2) + geom_line() + geom_vline(data = dt_plot_measures, aes(xintercept = day, lty = measure)) + facet_wrap(~ bundesland, scales = "free_y")
#p





# Mit der geglätteten Lograte?

layout(matrix(1:dtDEconfirmed[, uniqueN(bundesland)], nrow = 4))
lapply(dtDEconfirmed[, unique(bundesland)], function (x) acf(dtDEconfirmed[bundesland == x, lograte_smooth], na.action = na.omit, main = x))

f_lme_lograte <- as.character(f_lme)
f_lme_lograte[2] <- "lograte_smooth2"
f_lme_lograte <- formula(paste(f_lme_lograte[c(2, 1, 3)], collapse = ""))
mod_lme_lograte <- lmer(f_lme_lograte, data = dtDEconfirmed[!is.na(lograte_smooth2)])
summary(mod_lme_lograte)

dtDEconfirmed[!is.na(lograte_smooth2), yhat_lme_lograte := fitted(mod_lme_lograte)]

dt_plot <- melt(dtDEconfirmed[, .(bundesland, day, lograte_smooth2, estimate = yhat_lme_lograte)], id.vars = c("bundesland", "day"))

p <- ggplot(dt_plot, aes(x = day, y = value, col = variable)) + geom_hline(yintercept = 1, col = "red", lty = 2) + geom_line() + geom_vline(data = dt_plot_measures, aes(xintercept = day, lty = measure)) + facet_wrap(~ bundesland, scales = "free_y")
p




















# 
# schätzwerte für number_log aus modell?
# code in paket schnüren
# rplumber.io
# wetterdaten?
# bevölkerungsdichte?

## Anreize von Basti:

## "day" als Fixed Effect anstatt als Random Effect aufnehmen?
## Effekte ändern sich leicht, aber die Vorzeichen bleiben erhalten, Standardfehler ändern sich auch leicht
## Fixed Effect von day ist nicht signifikant, was auch zu erwarten wäre
## Daher ist die Überlegung, wenn es einen Tageseffekt gibt, ist der eher global oder auf Bundesland ebene ausgeprägt?
## Vorerst wird day als Random Effekt beibehalten
#f <- lograte_smooth2 ~ day + schulen_schliessung + veranstaltungen_verbot +  
#    kultureinrichtungen_schliessung + schutz_gef_personen + veranstaltungen_1000_verbot +  
#    kindertageseinrichtungen_schliessung + pandemieplan + grenzschliessung +  
#    (1 | bundesland)
#summary(lmer(f, data = dtDEconfirmed))

## Bundesländer/Beobachtungen erst ab mindestens 50 Fälle zulassen?
## Bis auf den Vorzeichenwechsel des inisignifikanten Effekts der Grenzschließung änder sich dadurch prinzipiell nichts... Wri verwenden weiterhin alle Daten vorerst!
#summary(lmer(f_lme_lograte, data = dtDEconfirmed[number >= 50]))


##layout(1:3)
##plot(dtDEconfirmed$day, residuals(mod_lme)); abline(0, 0, col = 2, lty = 2)
##plot(dtDEconfirmed[!is.na(number_log_smooth_diff), day], residuals(mod_lme_diff)); abline(0, 0, col = 2, lty = 2)
##plot(dtDEconfirmed[!is.na(number_log_smooth_diff2), day], residuals(mod_lme_diff2)); abline(0, 0, col = 2, lty = 2)

# Wunsch von Jörg
# Schätzwerte von number_log aus dem Modell berechnen

#corona_forecast <- dtDEconfirmed[, .(date, bundesland, number, number_log, lograte_smooth2, yhat_lme_lograte)]
##corona_forecast[, ab := shift(number_log, 1) - shift(number_log, 2)]
##corona_forecast[, bc := number_log - shift(number_log, 1)]
#corona_forecast[, i := 1:.N, by = bundesland]

#corona_forecast[, yhat := as.numeric(NA)]
#j <- 3
#a <- corona_forecast[i %in% (j - 2):j, yhat_lme_lograte * (shift(number_log, 1) - shift(number_log, 2)) + shift(number_log, 1)]
#a <- a[seq(3, length(a), by = 3)]
#corona_forecast[i == j, yhat := a]

#j <- 4
#a <- corona_forecast[i %in% (j - 2):j, yhat_lme_lograte * (shift(yhat, 1) - shift(number_log, 2)) + shift(yhat, 1)]
#a <- a[seq(3, length(a), by = 3)]
#corona_forecast[i == j, yhat := a]

#for (j in 5:10) {

#  a <- corona_forecast[i %in% (j - 2):j, yhat_lme_lograte * (shift(yhat, 1) - shift(yhat, 2)) + shift(yhat, 1)]
#  a <- a[seq(3, length(a), by = 3)]
#  corona_forecast[i == j, yhat := a]

#}
#corona_forecast[bundesland == "BY"]



# Datenexport für Dashboard

# Regressionskoeffizienten


coefs <- data.frame(summary(mod_lme_lograte)$coefficients[-1, c("Estimate", "Std. Error")])
coefs$measure_id <- rownames(coefs)
coefs <- merge(coefs, unique(DT_measures[, .(measure_id, measure = label)]), by = "measure_id")
coefs$measure_id <- NULL
coefs <- data.table(coefs)
setnames(coefs, "Std..Error", "se")
setnames(coefs, "Estimate", "estimate")
coefs[, lower := estimate - qnorm(0.975) * se]
coefs[, upper := estimate + qnorm(0.975) * se]
coefs <- merge(data.table(measure = DT_measures[, sort(unique(label))]), coefs[, .(measure, lower, estimate, upper)], on = "measure", all = TRUE)
coefs[, updated := update_date]

#####
##########
#    return(coefs)
#    })


#    # Die folgenden Datensätze wurden überÄnderung des Parameters update_date generiert, um Daten für die Entwicklung des Dashboards zu generieren
#    coefs <- rbindlist(coefs)
#    setorder(coefs, measure, updated)
#    coefs

#    fwrite(coefs, file = "data/measure_effect_estmates.csv", sep = ",", dec = ".", quote = TRUE)



#    pdf(file = "../plot_effects.pdf", height = 10, width = 10)

#    layout(1)
#    coefs_plot <- na.omit(coefs)
#    coefs_plot[measure == "Social Distancing (Kneipen, Abendprogramme, Kultur, Sport)", measure := "Social Distancing\n(Kneipen, Abendprogramme, Kultur, Sport)"]
#    coefs_plot[, measure := factor(measure)]
#    dates <- sort(unique(coefs_plot$updated))
#    offsets <- as.numeric(coefs_plot$measure)
#    k <- 2
#    par(las = 1, mar = c(3, 18, 1, 1) + 0.1)
#    plot(coefs_plot$updated, k * coefs_plot$estimate + offsets, axes = FALSE, pch = 16, ylim = c(min(offsets) - 0.5, max(offsets) + 0.5), xlab = NA, ylab = NA)
#    segments(x0 = coefs_plot$updated, x1 = coefs_plot$updated, y0 = offsets + k * coefs_plot$lower, y1 = offsets + k * coefs_plot$upper)
#    axis(1, at = as.numeric(dates), labels = dates)
#    axis(2, at = 1:nlevels(coefs_plot$measure), labels = levels(coefs_plot$measure))
#    segments(x0 = min(dates) - 1, x1 = max(dates) + 1, y0 = offsets, y1 = offsets, lty = 2, lwd = 0.2)
#    segments(x0 = min(dates) - 1, x1 = max(dates) + 1, y0 = c(c(0, offsets) + 0.5, y1 = c(0, offsets) + 0.5), lwd = 1.5)
#    #segments(x0 = rep(min(dates), 2), x1 = rep(max(dates), 2), y0 = c(0 - 0.5, max(offsets) + 0.5), y1 = c(0 - 0.5, max(offsets) + 0.5), lwd = 2)

#    dev.off()

##########
#####
