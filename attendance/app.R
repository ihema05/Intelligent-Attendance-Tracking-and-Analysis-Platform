library(shiny)
library(shinyjs)
library(DT)
library(dplyr)
library(ggplot2)
library(reticulate)

# ======================================================
# PYTHON ENV
# ======================================================
use_python(
  "C:/Users/ibrahim kamal/anaconda3/envs/faceenv/python.exe",
  required = TRUE
)

# ======================================================
# TEACHERS
# ======================================================
teachers <- data.frame(
  username = c("mobile","ai","os","math","stats","robo"),
  password = rep("1234", 6),
  course = c(
    "Prof. Training In Mobile App Programming",
    "Introduction To Artificial Intelligence",
    "Operating Systems",
    "Mathematical Foundations For Al",
    "Advanced Statistics",
    "Fundamentals Of Robotics"
  ),
  stringsAsFactors = FALSE
)

attendance_dir <- "C:/Users/ibrahim kamal/projects/attendance/attendance"

course_file <- function(course) {
  paste0(attendance_dir, "/", course, ".csv")
}

# ======================================================
# UI
# ======================================================
ui <- fluidPage(
  useShinyjs(),
  
  tags$head(
    tags$style(HTML("
      .login-container { display:flex; height:100vh; }
      .login-left {
        flex:2;
        background-image:url('login.png');
        background-size:cover;
        background-position:center;
      }
      .login-right { flex:1; padding:50px; }
    "))
  ),
  
  # ---------------- LOGIN ----------------
  div(
    id = "login",
    div(class="login-container",
        div(class="login-left"),
        div(class="login-right",
            h2("Teacher Login"),
            textInput("user","Username"),
            passwordInput("pass","Password"),
            actionButton(
              "login_btn",
              "Login",
              style="width:100%;background:#0066A2;color:white;font-size:16px;"
            )
        )
    )
  ),
  
  # ---------------- DASHBOARD ----------------
  hidden(
    div(
      id = "dashboard",
      sidebarLayout(
        sidebarPanel(
          h4("Course"),
          textOutput("course"),
          
          selectInput(
            "week",
            "Select Week",
            choices = 1:15,
            selected = 1
          ),
          
          actionButton(
            "start_cam",
            "Start Camera",
            style="background:green;color:white;width:100%;font-size:16px;"
          ),
          
          actionButton("refresh","Refresh"),
          
          hr(),
          h4("Statistics"),
          verbatimTextOutput("stats")
        ),
        
        mainPanel(
          tabsetPanel(
            tabPanel("Table", DTOutput("table")),
            tabPanel("Weekly", plotOutput("weekly")),
            tabPanel("Pie", plotOutput("pie"))
          )
        )
      )
    )
  )
)

# ======================================================
# SERVER
# ======================================================
server <- function(input, output, session){
  
  # ---------------- LOGIN ----------------
  observeEvent(input$login_btn, {
    m <- teachers[
      teachers$username == input$user &
        teachers$password == input$pass, ]
    
    if (nrow(m) == 1) {
      session$userData$course <- m$course
      hide("login")
      show("dashboard")
      output$course <- renderText(m$course)
    } else {
      showNotification("Invalid username or password", type = "error")
    }
  })
  
  # ---------------- LOAD / CREATE CSV ----------------
  attendance <- reactive({
    req(session$userData$course)
    
    f <- course_file(session$userData$course)
    
    if (!file.exists(f)) {
      d <- data.frame(
        StudentID = character(),
        Name = character(),
        Date = character(),
        Time = character(),
        Course = character(),
        Week = integer(),
        Confidence = numeric(),
        Present = integer(),
        stringsAsFactors = FALSE
      )
      write.csv(d, f, row.names = FALSE)
      return(d)
    }
    
    d <- read.csv(f, stringsAsFactors = FALSE)
    d$Week <- as.numeric(d$Week)
    d
  })
  
  # ---------------- START CAMERA ----------------
  observeEvent(input$start_cam, {
    course <- session$userData$course
    csv_path <- course_file(course)
    week <- input$week
    
    cmd <- paste0(
      'start "" cmd /c "cd /d C:/Users/ibrahim kamal/projects/attendance && ',
      '"C:/Users/ibrahim kamal/anaconda3/envs/faceenv/python.exe" ',
      '"recognize_attendance.py" ',
      '"', course, '" "', csv_path, '" "', week, '" & pause"'
    )
    
    shell(cmd, wait = FALSE)
    showNotification(paste("Camera started (Week", week, ")"))
  })
  
  # ---------------- TABLE ----------------
  output$table <- renderDT({
    datatable(attendance())
  })
  
  observeEvent(input$refresh, {
    output$table <- renderDT(datatable(attendance()))
  })
  
  # ---------------- ADVANCED STATISTICS ----------------
  output$stats <- renderPrint({
    d <- attendance()
    
    if (nrow(d) == 0) {
      cat("No attendance data yet.")
      return()
    }
    
    weekly_counts <- d %>% count(Week)
    
    mean_val <- mean(weekly_counts$n)
    median_val <- median(weekly_counts$n)
    
    mode_val <- weekly_counts$n[
      which.max(tabulate(match(weekly_counts$n, weekly_counts$n)))
    ]
    
    var_val <- var(weekly_counts$n)
    sd_val <- sd(weekly_counts$n)
    
    cat(
      "Total Records:", nrow(d), "\n",
      "Total Students:", length(unique(d$StudentID)), "\n",
      "Weeks Used:", length(unique(d$Week)), "\n\n",
      "Mean Attendance:", round(mean_val, 2), "\n",
      "Median Attendance:", median_val, "\n",
      "Mode Attendance:", mode_val, "\n",
      "Variance:", round(var_val, 2), "\n",
      "Standard Deviation:", round(sd_val, 2)
    )
  })
  
  # ---------------- WEEKLY ----------------
  output$weekly <- renderPlot({
    d <- attendance()
    if (nrow(d) == 0) return(NULL)
    
    ggplot(d, aes(x = factor(Week))) +
      geom_bar(fill = "darkorange") +
      xlab("Week") +
      ylab("Attendance Count") +
      theme_minimal()
  })
  
  # ---------------- PIE ----------------
  output$pie <- renderPlot({
    d <- attendance()
    if (nrow(d) == 0) return(NULL)
    
    p <- d %>% count(Week)
    
    ggplot(p, aes(x="", y=n, fill=factor(Week))) +
      geom_bar(stat="identity", width=1) +
      coord_polar("y") +
      theme_void() +
      labs(fill="Week")
  })
}

shinyApp(ui, server)
