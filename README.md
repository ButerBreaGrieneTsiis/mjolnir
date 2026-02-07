# mjölnir
Mjölnir is a Python package to schedule, track and visualise workouts. It is currently under development. It is primarily developed for Jim Wendler's 531. However, Mjölnir is developed to be rather abstract, so any workout template should be applicable.

## an overview of features

- create work-out templates
  - e.g. a "warm-up" template of 5 reps at 40%, 5 reps at 50%, 3 reps at 60%
  - e.g. a 531 template with week-dependent percentages
- create work-out schedules
  - schedule multiple weeks in advance, with day-dependent exercises
  - add exercices with one or multiple templates
- execute workouts using a streamlit dashboard
  - overview of all exercises; their sets, repetitions and even which plates to use
  - track sets by marking them as complete and/or filling in the attained number of repetitions
