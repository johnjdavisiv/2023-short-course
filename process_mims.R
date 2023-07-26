
library(MIMSunit)
library(tidyverse)


base_path <- 'C:\\temp_activity_data\\'
all_files <- list.files(base_path, pattern="*.csv")

save_path <- 'C:\\Users\\johnj\\Google Drive\\Research\\Obesity short course 2023\\data\\day_mims\\'


for (f in all_files){
  this_subject <- gsub("\\.csv$", "", f)
  print(this_subject)
  
  df <- read_csv(paste(base_path, f, sep=''), 
                 col_types = cols(
                   HEADER_TIME_STAMP = col_double(),
                   X = col_double(),
                   Y = col_double(),
                   Z = col_double()
                   ))
  #It reads correct you just dont' see it 
  df$HEADER_TIME_STAMP <- as.POSIXct(df$HEADER_TIME_STAMP, 
                                     origin = "1970-01-01", tz = "UTC")
  mims_data <- mims_unit(df, dynamic_range=c(-6,6), epoch='1 min')
  #"The sensor had arange and resolution of ±6 g and ±1 mg"
  
  save_name <- paste(this_subject, '_mims.csv', sep = '')
  sv_df <- mims_data %>% select(MIMS_UNIT)
  write.csv(sv_df, paste(save_path, save_name, sep=''), row.names=FALSE)
}











