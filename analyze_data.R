# Analyze 24hr activity data, demonstrating functional data-based analysis

library(tidyverse)
library(refund)

# --- Load in our files and main dataframe ----
main_df <- read_csv("data/main_df.csv")
all_files <- list.files("data/day_mims/", pattern="*.csv")

df_list <- list()
subject_df_list <- list()
Y <- matrix(data=NA,nrow=length(all_files),ncol=1440) #1440 minutes in a day

for (i in 1:length(all_files)){
  f <- all_files[i]
  this_subject <- gsub("\\_mims.csv$", "", f)
  
  this_df <- read_csv(paste("data/day_mims/", f, sep=''), show_col_types = FALSE) %>%
    mutate(hours = seq(0,24,length.out=1440),
           sub_code = this_subject)
  
  #Total activity
  this_subject_df <- main_df %>% filter(sub_code == this_subject) %>% 
    mutate(total_mims = sum(this_df$MIMS_UNIT))
  
  Y[i,] <- this_df$MIMS_UNIT #Drop in 24hr activity data
  df_list[[i]] <- this_subject_df #Slightly untidy but works
}

scalar_df <- bind_rows(df_list)

#Some preprocessing
scalar_df$sub_code <- factor(scalar_df$sub_code) #required for mgcv bs="re"
scalar_df$age10 <- scalar_df$age/10 #Scale so interpret as 10-yr change


scalar_df %>%
  ggplot(aes(x=age, y=total_mims, color=factor(is_male))) + 
  geom_point() + geom_smooth(method="lm") +
  scale_y_log10()

mod <- lm(log(total_mims) ~ age + is_male + age:is_male,
          data = scalar_df)

summary(mod)


Y_lp1 <- log(Y + 1) # Log(x=1) transform, better for Gaussian link function

y_ix <- seq(0,24, length.out = 1440) #Time index, hours (0-24)
k_int <- 64 #knots for global intercept
k_beta <- 64 #knots for functional effect including random effects
ctrl <- mgcv::gam.control(trace = TRUE) # "verbose=1"

mod_fx <- pffr(Y_lp1 ~ age10 + s(sub_code, bs="re"), 
               data = scalar_df,
               yind = y_ix, #Vector of time index, from 0 to 24 hours
               bs.yindex = list(bs="cp", k=k_beta, m=c(2,1)), #k cubic P-splines, 2nd order penalty
               bs.int = list(bs = "cp", k=k_int, m=c(2,1)), # ditto
               algorithm = "bam", 
               method = "fREML",
               control = ctrl,
               discrete = TRUE)

summary(mod_fx, re.test = FALSE)

plot(mod_fx)



resid_E = residuals(mod_fx)
cov_E <- t(resid_E) %*% resid_E

R_E <- cor(resid_E)

library(reshape2)
melted_R <- melt(R_E)
ggplot(data = melted_R, aes(x=Var2, y=Var1, fill=value)) + 
  geom_raster() + 
  scale_x_continuous(expand = c(0,0)) + 
  scale_y_reverse(expand = c(0,0)) + 
  scale_fill_gradientn(colors = c("#e41a1c", "white", "#377eb8"),
                         limits = c(-1, 1),
                         breaks = c(-1, 0, 1)) 


#Then predict for age.min to age.max(), remembering 10x transform

#back to original scale with exp() - 1

# ----------------------

#no resid

mod_s <- pffr(Y_lp1 ~ age10, 
               data = main_df,
               yind = y_ix, #Vector of time index, from 0 to 24 hours
               bs.yindex = list(bs="ps", k=k, m=c(2,1)), #k cubic P-splines, 2nd order penalty
               bs.int = list(bs = "ps", k=k, m=c(2,1)), # ditto
               algorithm = "bam", method = "fREML",
               control = ctrl,
               discrete = TRUE)

summary(mod_s, re.test = FALSE)

plot(mod_s)


resid_E = residuals(mod_s)

R_E <- cor(resid_E)

melted_R <- melt(R_E)


ggplot(data = melted_R, aes(x=Var2, y=Var1, fill=value)) + 
  geom_raster() + 
  scale_x_continuous(expand = c(0,0)) + 
  scale_y_reverse(expand = c(0,0)) + 
  scale_fill_gradientn(colors = c("#e41a1c", "white", "#377eb8"),
                       limits = c(-1, 1),
                       breaks = c(-1, 0, 1)) 







all_df <- bind_rows(df_list) 

summary_df <- all_df %>%
  group_by(sub_code) %>%
  summarize(total_MIMS = sum(MIMS_UNIT)) %>%
  left_join(main_df, by="sub_code")


summary_df %>%
  ggplot(aes(x=age, y=log(total_MIMS+1), color = subject_category)) + 
  geom_point() + geom_smooth(method="lm")


summary_df %>%
  ggplot(aes(x=log(total_MIMS))) + 
  geom_density()


mod <- lm(log(total_MIMS) ~ age + subject_category, data = summary_df)

summary(mod)


#%>% left_join(main_df, by="sub_code")


all_df %>% glimpse()

all_df %>% 
  ggplot(aes(x=hours, y=MIMS_UNIT, group=subject)) +
  geom_line(color="navy", alpha=0.4)


hour_seq <- seq(0, 24, by = 3)
formatted_hours <- sprintf("%02d:00", hour_seq)


this_df %>% 
  ggplot(aes(x=hours, y=MIMS_UNIT)) +
  geom_ribbon(aes(ymin=0, ymax=MIMS_UNIT), fill="navy", alpha=0.2) + 
  geom_line(color="navy", alpha=1, linewidth=0.5) + 
  ggtitle("24hrs of activity data, 1min summary") + 
  scale_y_continuous(name = 'Activity level (MIMS units)') + 
  scale_x_continuous(limits=c(0,24), breaks = hour_seq, expand = c(0.01,0),
                     labels = formatted_hours,
                     name = 'Time of day') +
  theme(plot.title = element_text(hjust=0.5))

  







