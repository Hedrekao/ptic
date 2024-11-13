## TODO:
- handle multiple predictions (multiple images) per same item -> just average predictions on the golang side
- display in frontend or just in csv why the prediction was made
    - either text containing in csv showing close calls
    - or return with prediction base64 image containing the hierarchy graph that will show the path and red line when the prediction was close
- use azure blob storage instead of local file system (with prod env)
- deploy everything (fe -> vercel, rest -> containers on azure)

