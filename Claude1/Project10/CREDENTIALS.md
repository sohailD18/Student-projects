# SkillSwap - Role-Based Access & Credentials

## Overview
SkillSwap has **3 distinct roles** with **NO OVERLAP** - completely separate pages and access levels:

1. **Admin** - Platform management and analytics
2. **Teacher** - Users who create skills and teach others
3. **Student** - Users who browse skills and book learning sessions

---

## IMPORTANT: Strict Role Separation

- **Public pages** are accessible to everyone
- **Admin pages** are ONLY accessible to admin/staff users
- **Teacher pages** are ONLY accessible to users who have created skills
- **Student pages** are ONLY accessible to users who haven't created skills yet

**No overlap between Teacher and Student features!**

---

## Page Structure by Role

### 🌐 PUBLIC PAGES (Accessible to All)
| Page | URL | Description |
|------|-----|-------------|
| Home | `/` | Landing page with stats and featured skills |
| Browse Skills | `/skills/` | View all available skills (read-only) |
| Skill Details | `/skills/<id>/` | View details of a specific skill |
| Login | `/users/login/` | Login page |
| Register | `/users/register/` | Registration page |

### 🔴 ADMIN ONLY PAGES
| Page | URL | Description |
|------|-----|-------------|
| Admin Dashboard | `/users/dashboard/admin/` | Platform overview with stats |
| Analytics Dashboard | `/admin/analytics/` | Detailed analytics with charts |
| Django Admin | `/admin/` | Full database management |

### 🟢 TEACHER ONLY PAGES
| Page | URL | Description |
|------|-----|-------------|
| Teacher Dashboard | `/users/dashboard/teacher/` | Manage skills, view teaching sessions, track earnings |
| My Teaching Sessions | `/teachers/sessions/` | View all teaching sessions with students |
| Create Skill | `/teachers/skills/create/` | Create a new skill listing |
| Update Skill | `/teachers/skills/<id>/update/` | Edit existing skill |
| Accept Session | `/teachers/sessions/<id>/accept/` | Accept pending booking requests |
| Complete Session | `/teachers/sessions/<id>/complete/` | Mark session as completed |
| Cancel Session | `/teachers/sessions/<id>/cancel/` | Cancel a session |

### 🔵 STUDENT ONLY PAGES
| Page | URL | Description |
|------|-----|-------------|
| Student Dashboard | `/users/dashboard/student/` | Track learning progress, view upcoming sessions |
| My Learning Sessions | `/students/sessions/` | View all learning sessions with teachers |
| Book Session | `/students/skills/<id>/book/` | Book a session with a teacher |
| Cancel Session | `/students/sessions/<id>/cancel/` | Cancel a booked session |
| Complete Session | `/students/sessions/<id>/complete/` | Mark session as completed + leave review |

### 📄 SHARED ACCESS PAGES (Both Teacher & Student)
| Page | URL | Description |
|------|-----|-------------|
| Session Detail | `/teachers/sessions/<id>/` OR `/students/sessions/<id>/` | View session details (teacher sees teacher view, student sees student view) |
| Profile Update | `/users/profile/update/` | Edit user profile |
| Dashboard Router | `/users/dashboard/` | Routes to appropriate dashboard based on role |

---

## Credentials & Access

### 1. ADMIN ROLE

**Credentials:**
- Username: `admin`
- Password: `1234`

**Pages Accessible:**
| Page | URL |
|------|-----|
| Admin Dashboard | `/users/dashboard/admin/` |
| Analytics Dashboard | `/admin/analytics/` |
| Django Admin | `/admin/` |
| Home | `/` |
| Browse Skills | `/skills/` |

**Role Badge:** 🔴 ADMIN ACCESS (Red gradient)

**After Login:** Redirects to Admin Dashboard (`/users/dashboard/admin/`)

---

### 2. TEACHER ROLE

**Demo Credentials:**
- Username: `john_developer`
- Password: `demo123`

**How to become a Teacher:**
Any user who creates at least one skill listing automatically becomes a teacher.

**Pages Accessible:**
| Page | URL |
|------|-----|
| Teacher Dashboard | `/users/dashboard/teacher/` |
| My Teaching Sessions | `/teachers/sessions/` |
| Create Skill | `/teachers/skills/create/` |
| Update Skill | `/teachers/skills/<id>/update/` |
| Profile | `/users/profile/update/` |
| Browse Skills | `/skills/` (read-only) |

**Features:**
- Create and manage skill listings
- View upcoming teaching sessions
- Accept/reject session requests
- Earn points from teaching
- Track teaching stats and earnings

**Role Badge:** 🟢 TEACHER (Green gradient)

**After Login:** Redirects to Teacher Dashboard (`/users/dashboard/teacher/`)

---

### 3. STUDENT ROLE

**Demo Credentials:**
- Any new registered user (without skills)

**How to become a Student:**
All new users start as students. When they create their first skill, they become teachers.

**Pages Accessible:**
| Page | URL |
|------|-----|
| Student Dashboard | `/users/dashboard/student/` |
| My Learning Sessions | `/students/sessions/` |
| Book Sessions | `/students/skills/<id>/book/` |
| Profile | `/users/profile/update/` |
| Browse Skills | `/skills/` |

**Features:**
- Browse and search skills by category
- Book sessions with teachers using points
- Track learning progress
- Earn badges for completing sessions
- View upcoming learning sessions

**Role Badge:** 🔵 STUDENT (Blue gradient)

**After Login:** Redirects to Student Dashboard (`/users/dashboard/student/`)

---

## Demo Users

### Admin User
| Username | Password | Role |
|----------|----------|------|
| admin | 1234 | Admin |

### Teacher Users (have skills created)
| Username | Password | Skills |
|----------|----------|--------|
| john_developer | demo123 | Python Programming, Web Development with Django |
| sarah_designer | demo123 | UI/UX Design Fundamentals, Logo Design Masterclass |
| mike_musician | demo123 | Acoustic Guitar, Music Theory Essentials |
| emma_chef | demo123 | Italian Cuisine, Baking Fundamentals |
| david_fitness | demo123 | Home Workout Guide, Nutrition for Healthy Living |
| lisa_linguist | demo123 | Conversational Spanish, French for Travelers |
| tom_artist | demo123 | Digital Illustration Basics |
| anna_writer | demo123 | Creative Writing Workshop |

### Student Users
Any new registration starts as a student. To create a student user, register a new account without creating any skills.

---

## Role Transitions

### Student → Teacher
When a student creates their first skill via `/teachers/skills/create/`, they automatically become a teacher and will be redirected to the Teacher Dashboard on next login.

**IMPORTANT:** Once a user becomes a teacher, they CANNOT go back to being a student only. They will always have access to teacher features.

### Admin → Any Role
Admins have access to all features. They can also create skills and act as teachers if desired.

---

## Dashboard Routing Logic

When a user visits `/users/dashboard/`, the system routes them based on:

1. **If user.is_staff or user.is_superuser** → Admin Dashboard (`/users/dashboard/admin/`)
2. **Else if user has skills_teaching** → Teacher Dashboard (`/users/dashboard/teacher/`)
3. **Else** → Student Dashboard (`/users/dashboard/student/`)

---

## URL Structure Summary

```
/                          # Home (Public)
/skills/                   # Browse Skills (Public)
/skills/<id>/              # Skill Details (Public)

/users/login/              # Login (Public)
/users/register/           # Register (Public)
/users/dashboard/          # Dashboard Router (Auth - redirects by role)
/users/profile/update/     # Edit Profile (Auth)

# ============ ADMIN ONLY ============
/users/dashboard/admin/    # Admin Dashboard (Admin only)
/admin/analytics/          # Analytics Dashboard (Admin only)
/admin/                    # Django Admin (Admin only)

# ============ TEACHER ONLY ===========
/users/dashboard/teacher/  # Teacher Dashboard (Teacher only)
/teachers/sessions/        # My Teaching Sessions (Teacher only)
/teachers/skills/create/   # Create Skill (Teacher only)
/teachers/skills/<id>/update/  # Update Skill (Teacher only)
/teachers/sessions/<id>/accept/  # Accept Session (Teacher only)
/teachers/sessions/<id>/complete/ # Complete Session (Teacher only)
/teachers/sessions/<id>/cancel/   # Cancel Session (Teacher only)

# ============ STUDENT ONLY ===========
/users/dashboard/student/  # Student Dashboard (Student only)
/students/sessions/        # My Learning Sessions (Student only)
/students/skills/<id>/book/     # Book Session (Student only)
/students/sessions/<id>/complete/ # Complete Session + Review (Student only)
/students/sessions/<id>/cancel/   # Cancel Session (Student only)
```

---

## Running the Project

1. **Start the server:**
   ```bash
   python manage.py runserver
   ```

2. **Access the application:**
   - Home: http://127.0.0.1:8000/
   - Login: http://127.0.0.1:8000/users/login/

3. **Seed demo data:**
   ```bash
   python manage.py seed_demo_data
   ```

4. **Create admin user:**
   ```bash
   python manage.py create_admin
   ```

---

## Key Points

✅ **Public pages** are accessible to everyone (home, browse skills)

✅ **Admin** has dedicated admin pages with platform analytics

✅ **Teacher** has separate `/teachers/` URLs for skill management and teaching sessions

✅ **Student** has separate `/students/` URLs for learning sessions and booking

✅ **NO OVERLAP** - Teachers and students have completely different page structures

✅ **Navigation** dynamically shows role-appropriate links

❌ Teachers CANNOT access student-specific pages like `/students/sessions/`

❌ Students CANNOT access teacher-specific pages like `/teachers/sessions/`

❌ The old `/sessions/` page NO LONGER EXISTS - replaced by `/teachers/sessions/` and `/students/sessions/`
