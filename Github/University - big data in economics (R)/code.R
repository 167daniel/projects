rm(list=ls())
options(scipen=999)
options(digits=5)
options(na.action = na.exclude)

library('car')
library('tidyverse')
library('sandwich')
library('lmtest')
library('writexl')
library('stargazer')
library('lfe')
library('stats')
library('reshape2')


# Load necessary libraries
library(dplyr)
library(zoo)
pacman::p_load(
  ggplot2,
  esquisse,BBmisc,ISLR,GGally,visdat, MASS, cluster ,shiny,data.table, gridExtra, tidyr, openxlsx,DT,BBmisc,shiny, ggforce,dplyr, flexclust, fpc, mclust
)


mydata<-read.csv("Train.csv")
mean(mydata$gameimportance, na.rm=TRUE)
mydata$gameimportance_fix <- ifelse(is.na(mydata$gameimportance), 6, mydata$gameimportance)
mydata$gameimportance <- ifelse(is.na(mydata$gameimportance), 6, mydata$gameimportance)


# Replace null values in permovingaverage with the mean of non-null values
mydata <- mydata %>%
  group_by(unique_id) %>%
  mutate(permovingaverage = ifelse(is.na(permovingaverage),
                                   mean(permovingaverage, na.rm = TRUE),
                                   permovingaverage)) %>%
  ungroup()
sum(is.na(mydata$permovingaverage))

mean(mydata$permovingaverage, na.rm=TRUE)
median(mydata$permovingaverage, na.rm=TRUE)

mydata$permovingaverage <- ifelse(is.na(mydata$permovingaverage), 11.093, mydata$permovingaverage)
# Replace the column "gameimportance" with "gameimportance_fix"
mydata$gameimportance <- mydata$gameimportance_fix

# Drop the "position" column
mydata$position <- NULL
mydata$gameimportance_fix <- NULL


# Create a new factor that combines player position (guard, forward, center)
mydata$player_position <- with(mydata, factor(ifelse(guard == 1, "guard", ifelse(forward == 1, "forward", "center"))))



# Custom color palette for the box plot
my_palette <- c("#1f78b4", "#33a02c", "#e31a1c")




#----------------Minutes distribution---------------------------
# Calculate the mean and median for the entire data
mean_minutes <- mean(mydata$minutes)
# Calculate the mean for the subset where minutes > 0
mean_minutes_subset <- mean(subset(mydata, minutes > 0)$minutes)

# Plot the data with labels for mean, median, and average (minutes > 0)
ggplot(data = subset(mydata, minutes > 0)) +
  aes(x = minutes) +
  geom_histogram(bins = 57, fill = "#112446", color = "black") +
  geom_vline(xintercept = mean_minutes, color = "blue", linetype = "dashed", size = 1) +
  geom_vline(xintercept = mean_minutes_subset, color = "green", linetype = "dashed", size = 1) +
  geom_text(aes(x = mean_minutes_subset, y = 10, label = paste("Avg (Minutes > 0):", round(mean_minutes_subset, 2))), color = "green", vjust = -1) +
  geom_text(aes(x = mean_minutes, y = 10, label = paste("Avg :", round(mean_minutes, 2))), color = "blue", vjust = -4) +
  labs(title = "Minutes distribution (Minutes > 0)", x = "Minutes", y= "Amount") +
  scale_x_continuous(breaks = seq(1, max(subset(mydata, minutes > 0)$minutes), 1)) +  
  theme(
    panel.grid.major = element_blank(),
    panel.grid.minor = element_blank(),
    panel.border = element_blank(),
    axis.line = element_line(colour = "black"),
    text = element_text(family = "Arial", size = 12),
    plot.title = element_text(size = 16, face = "bold"),
    axis.title = element_text(size = 14, face = "bold"),
    axis.text = element_text(size = 12)
  )
#----------------Game importance distribution---------------------------
# Calculate the mean and median for the entire data
mean_gameimportance <- mean(mydata$gameimportance)
# Calculate the mean for the subset where minutes > 0
# Plot the data with labels for mean, median, and average (minutes > 0)
ggplot(data =mydata) +
  aes(x = gameimportance) +
  geom_histogram(bins = 11, fill = "#112446", color = "black") +
  geom_vline(xintercept = mean_gameimportance, color = "blue", linetype = "dashed", size = 1) +
  geom_text(aes(x = mean_gameimportance, y = 10, label = paste("Avg :", round(mean_gameimportance, 2))), color = "blue", vjust = -1) +
  labs(title = "Game importance distribution", x = "Game importance", y= "Amount") +
  scale_x_continuous(breaks = seq(1, 11, 1)) +
  stat_bin(aes(label = ..count..), geom = "text", vjust = -0.5, color = "black", bins = 11) +
    theme(
    panel.grid.major = element_blank(),
    panel.grid.minor = element_blank(),
    panel.border = element_blank(),
    axis.line = element_line(colour = "black"),
    text = element_text(family = "Arial", size = 12),
    plot.title = element_text(size = 16, face = "bold"),
    axis.title = element_text(size = 14, face = "bold"),
    axis.text = element_text(size = 12)
  )
#----------------Coachfire---------------------------
ggplot(mydata)+
  aes(x = coachfire) +
  geom_histogram(binwidth = 1, color = "#FFFFFF", fill = "#112446") +
  labs(
    title = "Is coach in dagner to be fired ?",
    x = "Coach Fire",
    y = "Frequency"
  ) +
  scale_x_continuous(
    breaks = c(0, 1),
    labels = c("Not in danger", "In danger")
  ) +
  geom_text(stat = "count", aes(label = paste( ..count..)),
             vjust=1,color = "white") +
  theme_minimal(base_size = 14) +
  theme(
    plot.title = element_text(hjust = 0.5),
    axis.text = element_text(color = "#112446"),
    axis.title = element_text(color = "#112446"),
    axis.line = element_line(color = "#112446"),
    panel.grid.major = element_blank(),
    panel.grid.minor = element_blank(),
    panel.border = element_blank(),
    text = element_text(color = "#112446")
  )
#----------------Minuter per positon---------------------------
# Calculate the average for each position
average_data <- mydata %>%
  group_by(position) %>%
  summarise(average_minutes = mean(minutes))


ggplot(data=mydata) +
  aes(x = minutes, y = position) +
  geom_boxplot(fill = "#112446",color="#3565A2") +
  annotate("text", x = average_data$average_minutes, y = average_data$position,
           label = paste0("Average: ", sprintf("%.2f", average_data$average_minutes)),
              vjust = -4, color = "#3565A2", size = 3) +
    labs(title = "Mintues per position", x = "Minutes") +
  theme_minimal()+
  theme(
    panel.grid.major = element_blank(),
    panel.grid.minor = element_blank(),
    panel.border = element_blank(),
    axis.line = element_line(colour = "black"),
    text = element_text(family = "Arial", size = 12),
    plot.title = element_text(size = 16, face = "bold"),
    axis.title = element_text(size = 14, face = "bold"),
    axis.text = element_text(size = 12)
  )

#----------------------salry~draft rank--------------------------------
correlation <- cor(mydata$draftrank, mydata$salary)
ggplot(data=mydata)+
  aes(x = draftrank, y = salary) +
  geom_point(shape = 16, size = 1, colour = "#112446") +
  geom_smooth(method = "lm", se = FALSE, color = "#FF5733", linetype = "dashed") +
  geom_text(x = 2,vjust=-20, y = 1800, label = paste("Correlation:", round(correlation, 2)), 
            color = "#112446", hjust = 0, vjust = 0) +
  labs(title = "Draft Rank vs. Salary",
       x = "Draft Rank",
       y = "Salary") +
  
  scale_x_continuous(breaks = seq(1, 30, 1)) +
  theme_minimal(base_size = 14) +
  theme(plot.title = element_text(hjust = 0.5),
        panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        panel.border = element_blank(),
        axis.line = element_line(colour = "#112446"),
        text = element_text(color = "#112446"))
#-------------Draft rank-minutes-salary-------------


ggplot(data=mydata) +
  aes(x = draftrank, y = minutes, colour = salary) +
  geom_point(shape = 16, size = 1, alpha = 0.7) +  # Use a solid circle and slightly larger size
  scale_color_gradient(low = "blue", high = "red") +  # Custom color gradient
  scale_y_continuous(breaks = seq(0, 100, 20), limits = c(0, 60)) +
  geom_line(stat = "summary", fun = "mean", linetype = "dashed", size = 1) +
  theme_minimal() +
  theme(
    # Customize the appearance
    axis.text = element_text(size = 8, color = "black", family = "Arial"),
    axis.title = element_text(size = 14, color = "black", family = "Arial"),
    plot.title = element_text(size = 18, color = "black", family = "Arial", face = "bold"),
    legend.title = element_text(size = 14, color = "black", family = "Arial", face = "bold"),
    legend.text = element_text(size = 12, color = "black", family = "Arial"),
    legend.position = "right",  # Move legend to the right side of the plot
    plot.background = element_rect(fill = "white"),  # Set plot background to white
    panel.grid.major = element_line(colour = "lightgray"),  # Light gray major gridlines
    panel.grid.minor = element_blank(),  # Remove minor gridlines
    panel.border = element_rect(color = "black", fill = NA, size = 0.5)  # Add black panel border
  ) +
  labs(
    # Add informative labels and title
    x = "Draft Rank",
    y = "Minutes",
    color = "Salary",
    title = "Player Performance by Draft Rank and Salary",
    subtitle = "Relationship between draft rank, playing time, and salary",
    
  )
#-----------------heat-map ---------------------------


# Create a subset of the data with relevant columns
heatmap_data <- mydata[, c("minutes", "gameimportance", "draftrank", "permovingaverage", "salary", "bmi","pts","age","height", "ppm")]

# Calculate the correlation matrix
correlation_matrix <- cor(heatmap_data)

# Melt the correlation matrix to long format
correlation_df <- as.data.frame(as.table(correlation_matrix))


# Create the heatmap
ggplot(data = correlation_df, aes(x = Var1, y = Var2, fill = Freq)) +
  geom_tile(color = "white") +
  scale_fill_gradient2(low = "blue", mid = "purple", high = "red", midpoint = 0) +
  theme_minimal() +
  labs(
    x = "Variables",
    y = "Variables",
    title = "Correlation Heatmap: Minutes Played and numerical features",
    fill = "Correlation"
  )+
  geom_text(aes(label = ifelse((Freq > 0.5 | Freq < -0.5)& Freq!=1, round(Freq, 2), "")), size = 4, color = "black", vjust = 0.5)

#--------------------------------------------


p2 <- ggplot(mydata, aes(x = factor(overweight), y = minutes)) +
  geom_boxplot(alpha = 0.7, position = position_dodge(width = 0.75), width = 0.4, fill = my_palette[2], outlier.color = "red", outlier.shape = 1) +
  geom_point(data = mydata[mydata$minutes > quantile(mydata$minutes, 0.75) + 1.5 * IQR(mydata$minutes),], aes(x = factor(overweight), y = minutes, color = factor(overweight)), alpha = 0.7, size = 3) +
  stat_summary(fun = "mean", geom = "point", shape = 3, size = 3, color = "black", position = position_dodge(width = 0.75)) +
  ggtitle("Playing Time Distribution by Weight Status") +
  xlab("Weight Status") +
  ylab("Minutes") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 0, hjust = 0.5))

p3 <- ggplot(mydata, aes(x = factor(lottery_pick), y = minutes)) +
  geom_boxplot(alpha = 0.7, position = position_dodge(width = 0.75), width = 0.4, fill = my_palette[3], outlier.color = "red", outlier.shape = 1) +
  geom_point(data = mydata[mydata$minutes > quantile(mydata$minutes, 0.75) + 1.5 * IQR(mydata$minutes),], aes(x = factor(lottery_pick), y = minutes, color = factor(lottery_pick)), alpha = 0.7, size = 3) +
  stat_summary(fun = "mean", geom = "point", shape = 3, size = 3, color = "black", position = position_dodge(width = 0.75)) +
  ggtitle("Playing Time Distribution by Lottery Pick Status") +
  xlab("Lottery Pick Status") +
  ylab("Minutes") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 0, hjust = 0.5))


# Set custom labels for the factors

p2 <- p2 + scale_x_discrete(labels = c("Normal Weight", "Overweight"))
p3 <- p3 + scale_x_discrete(labels = c("Non-Lottery Pick", "Lottery Pick"))



# Display the updated plots with custom labels
combined_plot <- grid.arrange(p2, p3,  ncol = 1, widths = c(0.5), heights = c(4.5, 4.5))

# -----------------------------------------------------------------------------------

## same as before but by players

# Group by unique_id and calculate the average minutes for each player
player_summary <- mydata %>%
  group_by(unique_id) %>%
  summarize(mean_minutes = mean(minutes), player_position = first(player_position), overweight = first(overweight), lottery_pick = first(lottery_pick))

# Create small multiple plots for each relationship
p4 <- ggplot(player_summary, aes(x = player_position, y = mean_minutes)) +
  geom_boxplot(alpha = 0.7, position = position_dodge(width = 0.75), width = 0.4, fill = my_palette[1], outlier.color = "red", outlier.shape = 1) +
  geom_point(data = player_summary[player_summary$mean_minutes > quantile(player_summary$mean_minutes, 0.75) + 1.5 * IQR(player_summary$mean_minutes),], aes(x = player_position, y = mean_minutes, color = player_position), alpha = 0.7, size = 3) +
  stat_summary(fun = "mean", geom = "point", shape = 3, size = 3, color = "black", position = position_dodge(width = 0.75)) +
  ggtitle("Playing Time Distribution by Player Position") +
  xlab("Player Position") +
  ylab("Mean Minutes") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 0, hjust = 0.5))


p5 <- ggplot(player_summary, aes(x = factor(overweight), y = mean_minutes)) +
  geom_boxplot(alpha = 0.7, position = position_dodge(width = 0.75), width = 0.4, fill = my_palette[2], outlier.color = "red", outlier.shape = 1) +
  geom_point(data = player_summary[player_summary$mean_minutes > quantile(player_summary$mean_minutes, 0.75) + 1.5 * IQR(player_summary$mean_minutes),], aes(x = factor(overweight), y = mean_minutes, color = factor(overweight)), alpha = 0.7, size = 3) +
  stat_summary(fun = "mean", geom = "point", shape = 3, size = 3, color = "black", position = position_dodge(width = 0.75)) +
  ggtitle("Playing Time Distribution by Player Weight Status") +
  xlab("Weight Status") +
  ylab("Minutes") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 0, hjust = 0.5))


p6 <- ggplot(player_summary, aes(x = factor(lottery_pick), y = mean_minutes)) +
  geom_boxplot(alpha = 0.7, position = position_dodge(width = 0.75), width = 0.4, fill = my_palette[3], outlier.color = "red", outlier.shape = 1) +
  geom_point(data = player_summary[player_summary$mean_minutes > quantile(player_summary$mean_minutes, 0.75) + 1.5 * IQR(player_summary$mean_minutes),], aes(x = factor(lottery_pick), y = mean_minutes, color = factor(lottery_pick)), alpha = 0.7, size = 3) +
  stat_summary(fun = "mean", geom = "point", shape = 3, size = 3, color = "black", position = position_dodge(width = 0.75)) +
  ggtitle("Playing Time Distribution by Lottery Pick Status") +
  xlab("Lottery Pick Status") +
  ylab("Minutes") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 0, hjust = 0.5))


# Set custom labels for the factors
p5 <- p5 + scale_x_discrete(labels = c("Normal Weight", "Overweight"))
p6 <- p6 + scale_x_discrete(labels = c("Non-Lottery Pick", "Lottery Pick"))

# Display the updated plots with custom labels
combined_plot2 <- grid.arrange(p4, p5, p6, ncol = 1, widths = c(0.5), heights = c(3, 3, 3))
#---------------------------------------------------------


# Plot p7: Interaction between Player Position and Overweight Status vs. Mean Minutes
p7 <- ggplot(player_summary, aes(x = player_position, y = mean_minutes, fill = factor(overweight, labels = c("Normal Weight", "Overweight")))) +
  geom_boxplot(alpha = 0.7, position = position_dodge(width = 0.75), width = 0.4, outlier.color = "red", outlier.shape = 1) +
  ggtitle("Playing Time Distribution by Player Position and Weight Status") +
  xlab("Player Position") +
  ylab("Mean Minutes") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 0, hjust = 0.5))

# Plot p8: Interaction between Player Position and Lottery Pick Status vs. Mean Minutes
p8 <- ggplot(player_summary, aes(x = player_position, y = mean_minutes, fill = factor(lottery_pick, labels = c("Non-Lottery Pick", "Lottery Pick")))) +
  geom_boxplot(alpha = 0.7, position = position_dodge(width = 0.75), width = 0.4, outlier.color = "red", outlier.shape = 1) +
  ggtitle("Playing Time Distribution by Player Position and Lottery Pick Status") +
  xlab("Player Position") +
  ylab("Mean Minutes") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 0, hjust = 0.5))

# Plot p9: Interaction between Overweight Status and Lottery Pick Status vs. Mean Minutes
p9 <- ggplot(player_summary, aes(x = factor(overweight, labels = c("Normal Weight", "Overweight")), y = mean_minutes, fill = factor(lottery_pick, labels = c("Non-Lottery Pick", "Lottery Pick")))) +
  geom_boxplot(alpha = 0.7, position = position_dodge(width = 0.75), width = 0.4, outlier.color = "red", outlier.shape = 1) +
  ggtitle("Playing Time Distribution by Weight Status and Lottery Pick Status") +
  xlab("Weight Status") +
  ylab("Mean Minutes") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 0, hjust = 0.5))

combined_plot <- grid.arrange(p7, p8, p9, ncol = 1, heights = rep(3, 3,3))
# Combine the plots into a single visualization

# ------  garbage!!-----------------------------------------

# Convert the minutes column to float (numeric)
mydata$minutes <- as.numeric(mydata$minutes)

# Convert the data type of feature columns to numeric (if they are not already numeric)
mydata[, -1] <- lapply(mydata[, -1], as.numeric)

# Create the mydata_long dataframe
mydata_long <- pivot_longer(mydata, cols = -minutes, names_to = "Feature", values_to = "Value")

# Set the theme for better presentation
theme_set(theme_minimal())

filtered_data <- mydata_long %>%
  filter(!Feature %in% c("guard", "forward", "center", "player_position", "unique_id", "ppm_groups", "played", "lottery_pick", "overweight", "coachfire"))

# Create the grouped box plot with y-axis limited from 0 to 60
ggplot(filtered_data, aes(x = Value, y = Feature, fill = Feature)) +
  geom_boxplot() +
  xlim(0, 60) +
  labs(x = "Minutes", y = "Feature", title = "Grouped Box Plot of Features by Minutes")

#--------------------------------------------
# Divide minutes into groups


mydata$minutes_group <- cut(mydata$minutes, breaks = c(1, 10, 20, 30, 40, 60), labels = c("1-10", "11-20", "21-30", "31-40", "40+"))
mydata$minutes_group <- ifelse(mydata$minutes == 0, "Not played",cut(mydata$minutes, breaks = c(1, 10, 20, 30, 40, 60), labels = c("1-10", "11-20", "21-30", "31-40", "40+")))
ggplot(mydata) +
  aes(x = minutes_group, y = gameimportance, colour = factor(lottery_pick)) +
  geom_point(shape = 16, size = 3, alpha = 0.7) +  # Use a solid circle and slightly larger size
  scale_color_manual(values = c("#FF9900", "#0066FF"), name = "Lottery Pick") +  # Set manual colors for lottery_pick
  scale_x_discrete(labels = c("Not played", "11-20", "21-30", "31-40", "40+")) +  # Custom labels for x-axis
  scale_y_continuous(limits = c(0, 100), breaks = seq(0, 100, 10)) +  # Set y-axis limits and breaks
  labs(
    # Add informative labels and title
    x = "Minutes Group",
    y = "Game Importance",
    title = "Player Performance by Minutes Group, Game Importance, and Lottery Pick",
    subtitle = "the relationship between playing time, game importance, and lottery pick",
    caption = "Data source: Your Data Source"
  ) +
  theme_minimal() +
  theme(
    # Customize the appearance
    axis.text = element_text(size = 12, color = "black", family = "Arial"),
    axis.title = element_text(size = 14, color = "black", family = "Arial"),
    plot.title = element_text(size = 18, color = "black", family = "Arial", face = "bold"),
    plot.subtitle = element_text(size = 14, color = "black", family = "Arial", face = "italic"),
    legend.title = element_text(size = 14, color = "black", family = "Arial", face = "bold"),
    legend.text = element_text(size = 12, color = "black", family = "Arial"),
    legend.position = "right",  # Move legend to the right side of the plot
    legend.background = element_rect(fill = "white", color = "black", size = 0.5),  # Add border to the legend
    legend.key = element_rect(color = "transparent"),  # Remove border around legend keys
    plot.background = element_rect(fill = "#F5F5F5"),  # Set plot background to a light grayish color
    panel.grid.major = element_line(colour = "white", size = 0.5),  # White major gridlines
    panel.grid.minor = element_blank(),  # Remove minor gridlines
    panel.border = element_blank(),  # Remove panel border
    plot.caption = element_text(size = 10, color = "gray", family = "Arial")  # Caption style
  )

#--------------------mintues-positon--------------

#-----------------Section B: Finding causality-----------------
model_1<-lm(minutes~coachfire+gameimportance+coachfire*gameimportance,data=mydata)
summary(model_1)
model_1<-lm(minutes~coachfire+gameimportance+draftrank+permovingaverage+salary+guard+center+exp+coachfire*gameimportance,data=mydata)
summary(model_1)

#-----------------Section C: Creating clusters-----------------



# 1. Descriptive Statistics
# Compute mean, standard deviation, minimum, maximum, and other statistics for each player role
role_stats <- mydata %>%
  group_by(guard, forward, center) %>%
  summarize(
    mean_minutes = mean(minutes),
    sd_minutes = sd(minutes),
    min_minutes = min(minutes),
    max_minutes = max(minutes),
    mean_permovingaverage = mean(permovingaverage),
    sd_permovingaverage = sd(permovingaverage),
    mean_age = mean(age),
    sd_age = sd(age),
    mean_salary = mean(salary),
    sd_salary = sd(salary),
    mean_ppm = mean(ppm),
    sd_ppm = sd(ppm),
    mean_bmi = mean(bmi),
    sd_bmi = sd(bmi)
  )

# Print the descriptive statistics for each player role
print(role_stats)

#------------------------------------


# Calculate percentage of players in each age tier for each position group
mydata_summary <- mydata %>%
  group_by(guard, forward, center, age) %>%
  summarise(num_players = n()) %>%
  group_by(guard, forward, center) %>%
  mutate(percentage = (num_players / sum(num_players)) * 100)

# Define color palette for player position groups
my_palette <- c("#1f78b4", "#33a02c", "#e31a1c")  # Replace with your desired colors

# Line plot with filled curves to emphasize difference in percentage for each group in each age
line_plot_age_per_position <- ggplot(mydata_summary, aes(x = age, y = percentage, color = interaction(guard, forward, center), group = interaction(guard, forward, center))) +
  geom_ribbon(aes(ymin = 0, ymax = percentage, fill = interaction(guard, forward, center)), alpha = 0.2) + # Fill the area under the curve with the same color
  geom_point() +  # Add data points
  labs(x = "Age", y = "Percentage", title = "Percentage of Players in Each Age Tier by Player Position") +
  scale_color_manual(name = "Player Position", labels = c("Guard", "Forward", "Center"), values = my_palette) +
  scale_fill_manual(name = "Player Position", labels = c("Guard", "Forward", "Center"), values = my_palette) +  # Set the fill colors to match the line colors
  theme_minimal()


line_plot_age_per_position
# --------------------------
## pie plot


# Calculate the percentage of players who did not play for each position group
mydata_summary <- mydata %>%
  group_by(guard, forward, center) %>%
  summarise(num_played = sum(played == 1),
            num_not_played = sum(played == 0),
            total_players = n(),
            percentage_not_played = (num_not_played / total_players) * 100,
            percentage_played = (num_played / total_players) * 100)



# Calculate percentages for played and not played
mydata_summary$percentage_not_played <- with(mydata_summary, num_not_played / total_players * 100)
mydata_summary$percentage_played <- with(mydata_summary, num_played / total_players * 100)


# Set a larger plot size
options(repr.plot.width = 12, repr.plot.height = 5)

# Function to create pie plots with appropriate titles
plot_pie <- function(data, position) {
  labels <- c(
    paste0("Played (", round(data$percentage_played, 1), "%)"),
    paste0("Not Played (", round(data$percentage_not_played, 1), "%)")
  )
  values <- c(data$percentage_played, data$percentage_not_played)
  
  # Create a new data frame for the plot
  plot_data <- data.frame(labels = factor(labels, levels = labels), values)
  
  # Create the pie plot
  p <- ggplot(plot_data, aes(x = "", y = values, fill = labels)) +
    geom_bar(stat = "identity", width = 1) +
    coord_polar("y", start = 0) +
    theme_void() +
    labs(title = position) +  # Use position as the title
    theme(plot.title = element_text(hjust = 0.5))  # Center-align the title
  
  return(p)
}

# Create a list of pie plots for each record with appropriate titles
pie_plots <- lapply(1:nrow(mydata_summary), function(i) {
  data_row <- mydata_summary[i, ]
  position <- paste(
    ifelse(data_row$guard == 1, "Guard", ""),
    ifelse(data_row$forward == 1, "Forward", ""),
    ifelse(data_row$center == 1, "Center", "")
  )
  plot_pie(data_row, position)
})

# Arrange and print the pie plots using gridExtra
grid.arrange(grobs = pie_plots, ncol = 3, top = "Percentage of Players Played vs. Not Played by Position")


#------------ boxplots for kmeans -------

# Box plot for permovingaverage by player position
boxplot_permovingaverage <- ggplot(mydata, aes(x = player_position, y = permovingaverage, fill = player_position)) +
  geom_boxplot(alpha = 0.7, position = position_dodge(width = 0.75), width = 0.4, outlier.color = "black", outlier.shape = 1) +
  scale_fill_manual(values = my_palette, guide = FALSE) +
  theme(axis.title.x=element_blank(), axis.ticks.x=element_blank()) +  # Remove x-axis labels
  ggtitle("permovingaverage")

# Box plot for height by player position
boxplot_height <- ggplot(mydata, aes(x = player_position, y = height, fill = player_position)) +
  geom_boxplot(alpha = 0.7) +
  scale_fill_manual(values = my_palette, guide = FALSE) +
  theme(axis.title.x=element_blank(), axis.ticks.x=element_blank()) +  # Remove x-axis labels
  ggtitle("Height")

# Box plot for weight by player position
boxplot_weight <- ggplot(mydata, aes(x = player_position, y = weight, fill = player_position)) +
  geom_boxplot(alpha = 0.7) +
  scale_fill_manual(values = my_palette, guide = FALSE) +
  theme(axis.title.x=element_blank(), axis.ticks.x=element_blank()) +  # Remove x-axis labels
  ggtitle("Weight")

# Box plot for points by player position
boxplot_points <- ggplot(mydata, aes(x = player_position, y = pts, fill = player_position)) +
  geom_boxplot(alpha = 0.7) +
  scale_fill_manual(values = my_palette, guide = FALSE) +
  theme(axis.title.x=element_blank(), axis.ticks.x=element_blank()) +  # Remove x-axis labels
  ggtitle("Points")

# Box plot for BMI by player position
boxplot_bmi <- ggplot(mydata, aes(x = player_position, y = bmi, fill = player_position)) +
  geom_boxplot(alpha = 0.7, outlier.color = "black", outlier.shape = 1) +
  scale_fill_manual(values = my_palette, guide = FALSE) +
  theme(axis.title.x=element_blank(), axis.ticks.x=element_blank()) +  # Remove x-axis labels
  ggtitle("BMI")

# Combine the box plots using grid.arrange from gridExtra package
combined_boxplots <- grid.arrange(boxplot_permovingaverage, boxplot_height, boxplot_weight, boxplot_points, boxplot_bmi,
                                  ncol = 5, top = textGrob("Boxplots of Features for K-means", gp = gpar(fontsize = 14, fontface = "bold")),
                                  bottom = textGrob("Player Position", gp = gpar(fontsize = 12, fontface = "bold")))

# Print the combined box plots
print(combined_boxplots)

#------------ density height weight and points -------

# Density plot for weight by player position
weight_density_plot <- ggplot(mydata, aes(x = weight, fill = player_position)) +
  geom_density(alpha = 0.6) +
  scale_fill_manual(values = position_colors, guide = FALSE) +
  labs(title = "Density Plot of Weight by Player Position",
       x = "Weight",
       y = "Density") +
  theme_minimal()

# Density plot for height by player position
height_density_plot <- ggplot(mydata, aes(x = height, fill = player_position)) +
  geom_density(alpha = 0.6) +
  scale_fill_manual(values = position_colors, guide = FALSE) +
  labs(title = "Density Plot of Height by Player Position",
       x = "Height",
       y = "Density") +
  theme_minimal()

# Density plot for points by player position
points_density_plot <- ggplot(mydata, aes(x = pts, fill = player_position)) +
  geom_density(alpha = 0.6) +
  scale_fill_manual(values = position_colors, guide = FALSE) +
  labs(title = "Density Plot of Points by Player Position",
       x = "Points",
       y = "Density") +
  theme_minimal()

# Print the density plots
print(weight_density_plot)
print(height_density_plot)
print(points_density_plot)




#-------------------------------------------------------
#BMI
# Density plot for bmi by player position
density_bmi <- ggplot(mydata, aes(x = bmi, fill = player_position)) +
  geom_density(alpha = 0.5) +
  scale_fill_manual(values = position_colors, guide = FALSE) +
  labs(title = "BMI by Player Position",
       x = "BMI",
       y = "Density") +
  theme_minimal()


#permoving average
ggplot(mydata, aes(x = player_position, y = permovingaverage, fill = player_position)) +
  geom_boxplot(alpha = 0.7, outlier.color = "black", outlier.shape = 1) +
  scale_fill_manual(values = position_colors, guide = FALSE) +
  labs(title = "BMI by Player Position",
       x = "Player Position",
       y = "permovingaverage") +
  theme_minimal()





#------------------------------------------------------------
# lottery pick

# Create a bar plot for lottery_pick by player_position
lottery_pick_plot <- ggplot(mydata, aes(x = player_position, fill = factor(lottery_pick))) +
  geom_bar(position = "dodge") +
  scale_fill_manual(values = c("blue", "gray"), labels = c("No Lottery Pick", "Lottery Pick")) +
  labs(title = "Proportion of Players with/without Lottery Picks by Player Position",
       x = "Player Position",
       y = "Count") +
  theme_minimal()

# Print the bar plot
print(lottery_pick_plot)


# Calculate the percentage of players with and without overweight by player position
percentage_data <- mydata %>%
  group_by(player_position, overweight) %>%
  summarize(count = n()) %>%
  group_by(player_position) %>%
  mutate(percentage = count / sum(count) * 100)

# Create a bar plot for lottery_pick by player_position
overweight_pick_plot <- ggplot(percentage_data, aes(x = player_position, y = percentage, fill = factor(overweight))) +
  geom_bar(stat = "identity", position = "dodge") +
  scale_fill_manual(values = c("blue", "gray"), labels = c("No overweight", "Overweight")) +
  labs(title = "Proportion of Players with/without overweight by Player Position",
       x = "Player Position",
       y = "Percentage") +
  theme_minimal()

# Print the bar plot
print(overweight_pick_plot)

#--------------------- doing kmmaens--------------------
# Select the relevant columns for k-means
kmeans_data <- mydata %>%  dplyr::select(bmi, weight, height, pts, minutes, player_position, permovingaverage)

# Apply IQR capping for BMI in the forward position
forward_data <- subset(kmeans_data, player_position == "forward")
bmi_iqr <- IQR(forward_data$bmi)
outlier_threshold <- 1.5 * bmi_iqr
outliers_low <- forward_data$bmi < (quantile(forward_data$bmi, 0.25) - outlier_threshold)
outliers_high <- forward_data$bmi > (quantile(forward_data$bmi, 0.75) + outlier_threshold)
forward_data$bmi[outliers_low] <- quantile(forward_data$bmi, 0.25) - outlier_threshold
forward_data$bmi[outliers_high] <- quantile(forward_data$bmi, 0.75) + outlier_threshold
kmeans_data$bmi <- ifelse(kmeans_data$player_position == "forward", forward_data$bmi, kmeans_data$bmi)

# Log transformation of capped points (adding a small value to avoid issues with zero points)
kmeans_data <- kmeans_data %>%
  mutate(log_pts = log(pts + 1))

# Winsorize the height variable for the center position
center_height <- kmeans_data$height[kmeans_data$player_position == "center"]
pct_5 <- quantile(center_height, 0.05)
pct_95 <- quantile(center_height, 0.95)

kmeans_data$height_capped_center <- ifelse(kmeans_data$player_position == "center", 
                                           pmax(pct_5, pmin(center_height, pct_95)), 
                                           kmeans_data$height)


kmeans_data$arcsinh_permovingaverage <- asinh(kmeans_data$permovingaverage)


ggplot(kmeans_data, aes(y = arcsinh_permovingaverage, x = player_position)) +
  geom_boxplot() +
  labs(title = "Box Plot of Log-Adjusted permovingaverage by Player Position",
       y = "Log-Adjusted permovingaverage",
       x = "Player Position") +
  theme_minimal()

# drop
kmeans_data <- kmeans_data %>%
  dplyr::select(-player_position, -pts, -height, -log_pts, -minutes, -arcsinh_permovingaverage)

# Scale the data
scaled_data <- scale(kmeans_data)

# Convert the scaled data to a data frame
scaled_data <- as.data.frame(scaled_data)

# perform kmeans
kmeans_result <- kmeans(scaled_data, centers = 3)
cluster_assignments <- kmeans_result$cluster



# Assuming kmeans_result contains the clustering results
ari <- adjustedRandIndex(kmeans_result$cluster, as.numeric(mydata$player_position))


# Create the scatter plot with different colors for each position and cluster
ggplot(mydata, aes(x = weight, y = height, color = as.factor(cluster_assignments))) +
  geom_point(size = 3) +
  scale_color_discrete(name = "Cluster", labels = c("Cluster 1", "Cluster 2", "Cluster 3")) +
  labs(title = "K-means Clustering of Player Positions",
       x = "Weight",
       y = "Height") +
  theme_minimal()


#-----------------------------
k_means<-as.data.table(mydata)
k_means<-k_means[,-c("index","position","unique_id","permovingaverage")]
kmeans <- kmeans(k_means, centers = 3)
kmeans$centers

# Plot data points with cluster assignments
ggplot(k_means, aes(x = minutes, y = gameimportance, color = as.factor(kmeans$cluster))) +
  geom_point() +
  labs(title = "K-means Clustering",
       x = "minutes",
       y = "draftrank",
       color = "Cluster") +
  theme_minimal()

# Plot cluster centers as well
ggplot(k_means, aes(x = minutes, y = coachfire, color = as.factor(kmeans$cluster))) +
  geom_point() +
  geom_point(data = as.data.frame(kmeans$centers), aes(x = Column1, y = Column2),
             color = "black", size = 4, shape = 3) +  # Use shape 3 (triangle) for cluster centers
  labs(title = "K-means Clustering with Cluster Centers",
       x = "Column1",
       y = "Column2",
       color = "Cluster") +
  theme_minimal()


# Select relevant attributes for clustering
selected_attributes <- mydata %>%
  select(guard, forward, center, minutes, coachfire, gameimportance, draftrank, permovingaverage,pts)

# Impute missing values with the mean of each column
selected_attributes <- na.aggregate(selected_attributes)

# Standardize the data
standardized_data <- scale(selected_attributes)

# Perform k-means clustering with 3 clusters (you can change the number of clusters as per your requirement)
num_clusters <- 3
kmeans_model <- kmeans(standardized_data, centers = num_clusters)

# Add cluster labels to the original data frame
mydata$cluster <- kmeans_model$cluster

ggplot(mydata, aes(x = player_position, fill = factor(cluster))) +
  geom_bar(position = "dodge") +
  labs(title = "Cluster Distribution by Player Position",
       x = "Player Position",
       y = "Count",
       fill = "Cluster") +
  theme_minimal()
#-----------------Section D: Predicting the unknown-----------------
esquisse::esquisser()
mydata_table <- data.table(mydata)
mydata_table<-mydata_table[,-c("position")]
correlation_matrix <- cor(mydata_table, use = "complete.obs")
view(correlation_matrix)

