library(rapportools)
library(readr)
library(dplyr)
library(ggplot2)
library(scales)
library("grid")
up <- function(x) {
  result <- mean(x) + qnorm(0.975)*sd(x)/sqrt(length(x))
  return(result)
}
down <- function(x) {
  result <- mean(x) - qnorm(0.975)*sd(x)/sqrt(length(x))
  return(result)
}


data <- readr::read_delim("./all_tffs_stat.txt", delim=" ", col_names = FALSE, trim_ws=TRUE)
data <- as.data.frame(data)
colnames(data) <- c("N","RDD","TF","SEED",
                    "Max_order",
                    "MAE",
                    "Normalized_MAE",
                    "F1_Min",
                    "F1_Max",	
                    "F2_Min",	
                    "F2_Max",	
                    "MAE-GO_Orig",
                    "Normalized_MAE-GO_Orig",
                    "GO_Orig_MAE-GO_Trunc",
                    "Normalized_MAE-GO_Trunc",
                    "GO_Trunc",
                    "Ranking",
                    "MAE",
                    "Preserved_GO")
data <- data[,-c(20)]

png("./All.png", width=120, height = 280, units = "cm", res = 300, bg = "transparent")
df <- melt(data = data, id.vars = c("N","RDD","TF","SEED","Max_order"), measure.vars = c(
                                                                             "MAE",
                                                                             "Normalized_MAE",
                                                                             "F1_Min",
                                                                             "F1_Max",	
                                                                             "F2_Min",	
                                                                             "F2_Max",	
                                                                             "MAE-GO_Orig",
                                                                             "Normalized_MAE-GO_Orig",
                                                                             "GO_Orig_MAE-GO_Trunc",
                                                                             "Normalized_MAE-GO_Trunc",
                                                                             "GO_Trunc",
                                                                             "Ranking",
                                                                             "MAE",
                                                                             "Preserved_GO"))



pos <- position_dodge(0.9)
ggplot(df, aes(x = factor(Max_order), y= value, fill = factor(N))) +
  geom_violin(alpha = 0.45, position = pos) +
  geom_boxplot(width = .4, 
               fatten = NULL, 
               alpha = 0.75,
               position = pos, outlier.size = 0.1) +
  stat_summary(fun = "mean", 
               geom = "point", 
               position = pos) +
  stat_summary(fun.data = "mean_se", 
               geom = "errorbar", 
               width = .1,
               position = pos) +
  scale_fill_brewer(palette = "Dark2") +
  #facet_wrap(  ~ N , scales="free", ncol = 5) +
  facet_grid( variable ~ N ) +
  theme_bw() +
  scale_y_log10() +
  theme(
    legend.key.width = unit(2, "cm"),
    legend.title=element_text(size=20),
    axis.text.x = element_text(angle = 90, hjust = 1),
    axis.text=element_text(size=24),
    axis.title=element_text(size=24),
    strip.text = element_text(size=24),
    legend.text=element_text(size=20),
    legend.position="bottom",
    panel.grid.minor = element_blank()
  )
dev.off()


png("./All.png", width=120, height = 20, units = "cm", res = 300, bg = "transparent")
df <- data

pos <- position_dodge(0.9)
ggplot(df, aes(x = factor(Max_order), y= Normalized_MAE, fill = factor(N))) +
  geom_violin(alpha = 0.45, position = pos) +
  geom_boxplot(width = .4, 
               fatten = NULL, 
               alpha = 0.75,
               position = pos, outlier.size = 0.1) +
  stat_summary(fun = "mean", 
               geom = "point", 
               position = pos) +
  stat_summary(fun.data = "mean_se", 
               geom = "errorbar", 
               width = .1,
               position = pos) +
  scale_fill_brewer(palette = "Dark2") +
  #facet_wrap(  ~ N , scales="free", ncol = 5) +
  facet_grid( ~ N ) +
  theme_bw() +
  scale_y_log10() +
  theme(
    legend.key.width = unit(2, "cm"),
    legend.title=element_text(size=20),
    axis.text.x = element_text(angle = 90, hjust = 1),
    axis.text=element_text(size=24),
    axis.title=element_text(size=24),
    strip.text = element_text(size=24),
    legend.text=element_text(size=20),
    legend.position="bottom",
    panel.grid.minor = element_blank()
  )
dev.off()

