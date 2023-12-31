# Wearable Sensors for Physical Activity: Collection and Analysis Considerations

Slides, code, and data to support my talk, *Tracking physical activity with wearable sensors: Considerations for data collection and analysis*, for the 2023 Mathematical Sciences in Obesity Research short course.  

**Code output:** [Rmarkdown html here](https://johnjdavisiv.github.io/2023-short-course/)  

The code shows a worked example of analyzing 24-hour accelerometry data, using a subset of the open-access [Long-term Movement Monitoring Database](https://physionet.org/content/ltmm/1.0.0/). I've already summarized the raw 100 Hz acceleration data and summarized it in one-minute epochs as "MIMS units" via the `MIMSunit` R package ([link here](https://github.com/mHealthGroup/MIMSunit)). MIMS units are very similar to "counts" available from Actigraph devices, but they have some technical and practical advantages. Check out [the paper](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8301210/) for more on MIMS units.  

This is an *educational* analysis meant to be simple and feasible on a lower-end laptop, which put some hard constraints on how much and how complex of a dataset we can work with. It also skips over some of the finer points that really do matter in research studies, like what to do about non-wear-time and other sources of missingness in your data.  Also, in part because of the small size of the dataset, we don't get particularly interesting or insightful results. Repeat this analysis on the entire NHANES cohort and it'd probably be a different story (both in terms of interestingness and computational cost).  

The present dataset consists of waist-worn accelerometer data from one 24-hour day (midnight to midnight) from 50 older adults. These older adults were classified as "fallers" (people who had a history of falls) and "controls" (no history of falls). This is a subset of the larger LTMMD; I preprocessed only subjects with a reasonable amount of wear time in their first 24-hour day of device wear. The full dataset is larger (~80 subjects) and has multiple days of data from each subject.  

The preprocessing into MIMSunits data is done in a mix of Python and R; the true raw data are not uploaded here because of file size constraints on GitHub--you'll need the original PhysioNet dataset to reproduce the whole analysis.  