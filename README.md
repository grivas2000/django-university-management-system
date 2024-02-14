# University Management System

## Description

University Management System, built on the Django framework with SQLite3, serves as a robust platform for managing university courses, students and professors. With tailored features and access levels, it caters to various user roles, including administrators, professors and students.

## User Roles and Features

### 1. Administrator

Admins wield complete control over the application and its data. Their capabilities encompass:

- Viewing all student, professor and course details.
- Adding, modifying or removing student, professor and course records.
- Assigning or unassigning professors to courses.
- Enrolling or unenrolling students in courses.
- Gaining insights into which professors are assigned to specific courses and which students are enrolled in each course.

### 2. Professor

Professors have access limited to the courses they are assigned to. Their functionalities include:

- Viewing the courses they are responsible for.
- Accessing the list of students enrolled in their courses.
- Monitoring students' pass or fail statuses for their respective courses.
- Granting or revoking a student's pass status by providing or removing their signature.

### 3. Student

Students enjoy access to information concerning their own courses and academic status. Their capabilities consist of:

- Viewing the courses they are currently enrolled in.
- Checking their pass or fail status for courses.
- Enrolling or unenrolling themselves from courses.

## Setup

To build and run the application, ensure you have Python and SQLite3 installed on your machine. Then, proceed with the following steps:

1. Clone the repository from GitHub.
2. Navigate to the project's root directory.
3. Install the required dependencies using `pip install -r requirements.txt`.
4. Execute Django migrations to set up your database with `python manage.py migrate`.
5. Start the Django development server with `python manage.py runserver`.

You can access the application at `localhost:8000` in your web browser.

I've included two fixture files named `'fixtures.json'` and `'fixtures2.json'` for your convenience in populating your application with initial data. To load it:

- Run `python manage.py loaddata fixtures.json fixtures2.json` from the project's root directory via the terminal.
