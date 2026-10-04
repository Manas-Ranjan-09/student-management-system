/**
 * Admin Dashboard & CRUD Operations Controller
 */

let deptChart = null;
let cachedDepartments = [];
let cachedCourses = [];
let cachedStudents = [];

// Ensure user is authorized as Admin
const currentUser = AUTH.requireAuth('admin');
if (currentUser) {
    document.getElementById('admin-name').innerText = currentUser.name || currentUser.username;
}

function debounce(func, delay = 300) {
    let timer;
    return function (...args) {
        clearTimeout(timer);
        timer = setTimeout(() => func.apply(this, args), delay);
    };
}

function switchSection(sectionId, navElement = null) {
    document.querySelectorAll('.section-view').forEach(s => s.classList.remove('active'));
    const target = document.getElementById(`section-${sectionId}`);
    if (target) target.classList.add('active');

    if (navElement) {
        document.querySelectorAll('.sidebar-nav .nav-item').forEach(n => n.classList.remove('active'));
        navElement.classList.add('active');
    }

    const titleMap = {
        dashboard: ['Administrator Dashboard', 'Overview of campus academic activity and metrics'],
        students: ['Students Directory', 'Manage student profiles, enrollments, and academic credentials'],
        departments: ['Departments Management', 'Configure academic departments and faculties'],
        courses: ['Courses & Programs', 'Manage degrees, branches, and durations'],
        results: ['Semester Examination Results', 'Publish, review, and compute semester grade statements']
    };

    if (titleMap[sectionId]) {
        document.getElementById('page-title').innerText = titleMap[sectionId][0];
        document.getElementById('page-subtitle').innerText = titleMap[sectionId][1];
    }

    // Trigger loads
    if (sectionId === 'dashboard') loadDashboard();
    if (sectionId === 'students') loadStudents();
    if (sectionId === 'departments') loadDepartments();
    if (sectionId === 'courses') loadCourses();
    if (sectionId === 'results') loadResults();
}

// ---------------- DASHBOARD ----------------
async function loadDashboard() {
    try {
        const data = await API.get('/api/dashboard/admin/');
        document.getElementById('dash-total-students').innerText = data.total_students;
        document.getElementById('dash-total-depts').innerText = data.total_departments;
        document.getElementById('dash-total-courses').innerText = data.total_courses;
        document.getElementById('dash-total-results').innerText = data.total_results;

        // Render Recent Table
        const recentTbody = document.querySelector('#recent-students-table tbody');
        if (data.recent_students && data.recent_students.length > 0) {
            recentTbody.innerHTML = data.recent_students.map(s => `
                <tr>
                    <td>
                        <div style="display:flex; align-items:center; gap: 0.75rem;">
                            <div style="width:36px; height:36px; border-radius:50%; background:var(--primary-light); color:var(--primary); display:flex; align-items:center; justify-content:center; font-weight:700;">
                                ${s.name.charAt(0)}
                            </div>
                            <div>
                                <div style="font-weight:700;">${s.name}</div>
                                <div style="font-size:0.8rem; color:var(--text-muted);">${s.email}</div>
                            </div>
                        </div>
                    </td>
                    <td><strong>${s.roll_number}</strong></td>
                    <td><span class="badge-custom badge-primary">${s.department_code || 'N/A'}</span></td>
                    <td>${s.course_name || 'N/A'}</td>
                    <td><span class="badge-custom badge-warning">Sem ${s.semester}</span></td>
                </tr>
            `).join('');
        } else {
            recentTbody.innerHTML = '<tr><td colspan="5" style="text-align:center; color:var(--text-muted);">No records available.</td></tr>';
        }

        // Render Chart.js
        renderDeptChart(data.dept_distribution || []);
    } catch (err) {
        UI.showToast('Failed to load dashboard metrics: ' + err.message, 'error');
    }
}

function renderDeptChart(distribution) {
    const ctx = document.getElementById('deptDistributionChart');
    if (!ctx) return;

    if (deptChart) {
        deptChart.destroy();
    }

    const labels = distribution.map(d => d.name);
    const counts = distribution.map(d => d.count);

    deptChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Enrolled Students',
                data: counts,
                backgroundColor: [
                    'rgba(59, 130, 246, 0.85)',
                    'rgba(139, 92, 246, 0.85)',
                    'rgba(16, 185, 129, 0.85)',
                    'rgba(245, 158, 11, 0.85)',
                    'rgba(6, 182, 212, 0.85)'
                ],
                borderRadius: 8,
                borderSkipped: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { stepSize: 1 }
                }
            }
        }
    });
}

// ---------------- CACHE DROPDOWNS ----------------
async function ensureMetadata() {
    if (cachedDepartments.length === 0 || cachedCourses.length === 0) {
        const [depts, courses] = await Promise.all([
            API.get('/api/departments/'),
            API.get('/api/courses/')
        ]);
        cachedDepartments = depts;
        cachedCourses = courses;

        // Populate student filter dropdown
        const filterDept = document.getElementById('student-filter-dept');
        if (filterDept) {
            filterDept.innerHTML = '<option value="">All Departments</option>' +
                depts.map(d => `<option value="${d.id}">${d.name}</option>`).join('');
        }
    }
}

// ---------------- STUDENTS ----------------
async function loadStudents() {
    await ensureMetadata();
    const query = document.getElementById('student-search-input')?.value.trim();
    const dept = document.getElementById('student-filter-dept')?.value;
    const sem = document.getElementById('student-filter-sem')?.value;

    try {
        const students = await API.get('/api/students/', { q: query, department: dept, semester: sem });
        cachedStudents = students;
        const tbody = document.getElementById('students-tbody');

        if (students.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; padding: 2rem; color:var(--text-muted);"><i class="fas fa-search me-2"></i>No students found matching your criteria.</td></tr>';
            return;
        }

        tbody.innerHTML = students.map(s => `
            <tr>
                <td>
                    <div style="display:flex; align-items:center; gap: 0.75rem;">
                        <div style="width:40px; height:40px; border-radius:50%; background:var(--primary-light); color:var(--primary); display:flex; align-items:center; justify-content:center; font-weight:700;">
                            ${s.name.charAt(0)}
                        </div>
                        <div>
                            <div style="font-weight:700;">${s.name}</div>
                            <div style="font-size:0.8rem; color:var(--text-muted);">${s.email}</div>
                        </div>
                    </div>
                </td>
                <td><strong>${s.roll_number}</strong></td>
                <td>${s.registration_number}</td>
                <td><span class="badge-custom badge-primary">${s.department_code || 'N/A'}</span></td>
                <td>${s.course_name || 'N/A'}</td>
                <td><span class="badge-custom badge-warning">Sem ${s.semester}</span></td>
                <td style="text-align: right;">
                    <button class="action-icon-btn view" title="View Profile Report" onclick="viewStudentDetail(${s.id})">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="action-icon-btn edit" title="Edit Student" onclick="openEditStudentModal(${s.id})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="action-icon-btn delete" title="Delete Student" onclick="deleteStudent(${s.id}, '${s.name}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    } catch (err) {
        UI.showToast('Error loading students: ' + err.message, 'error');
    }
}

async function viewStudentDetail(studentId) {
    try {
        const student = await API.get(`/api/students/${studentId}/`);
        const results = await API.get('/api/results/', { student: studentId });

        // Calculate CGPA
        const cgpa = results.length > 0 ? results[0].cgpa : '0.00';

        const modalHtml = `
            <div class="modal-backdrop-custom show" id="student-detail-modal">
                <div class="modal-content-custom" style="max-width: 750px; padding: 2rem;">
                    <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid var(--border-glass); padding-bottom:1rem; margin-bottom:1.5rem;">
                        <h4 style="margin:0;"><i class="fas fa-id-card me-2 text-primary"></i>Student Profile Details</h4>
                        <button onclick="document.getElementById('student-detail-modal').remove()" style="background:none; border:none; font-size:1.25rem; cursor:pointer; color:var(--text-muted);">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>

                    <!-- Header card -->
                    <div class="glass-card" style="padding:1.25rem; display:flex; justify-content:space-between; align-items:center; margin-bottom:1.5rem;">
                        <div style="display:flex; gap:1rem; align-items:center;">
                            <div style="width:54px; height:54px; border-radius:50%; background:var(--primary); color:white; display:flex; align-items:center; justify-content:center; font-size:1.5rem; font-weight:700;">
                                ${student.name.charAt(0)}
                            </div>
                            <div>
                                <h3 style="margin:0;">${student.name}</h3>
                                <div style="color:var(--text-secondary); font-size:0.9rem;">Roll No: <strong>${student.roll_number}</strong> | ID: <strong>${student.student_id}</strong></div>
                            </div>
                        </div>
                        <div style="text-align:right;">
                            <div style="font-size:0.8rem; font-weight:700; color:var(--text-muted); text-transform:uppercase;">Overall CGPA</div>
                            <h2 style="color:var(--primary); margin:0;">${cgpa}</h2>
                        </div>
                    </div>

                    <!-- Academic Info Grid -->
                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:1rem; margin-bottom:1.5rem; font-size:0.9rem;">
                        <div><strong>Department:</strong> ${student.department_name} (${student.department_code})</div>
                        <div><strong>Course:</strong> ${student.course_name}</div>
                        <div><strong>Current Semester:</strong> Semester ${student.semester}</div>
                        <div><strong>Academic Year:</strong> ${student.academic_year}</div>
                        <div><strong>Email:</strong> ${student.email}</div>
                        <div><strong>Phone:</strong> ${student.phone || 'N/A'}</div>
                    </div>

                    <!-- Academic Record Table -->
                    <h5 style="margin-bottom:0.75rem;"><i class="fas fa-award me-2 text-warning"></i>Examination Results</h5>
                    <div style="max-height:220px; overflow-y:auto; border:1px solid var(--border-glass); border-radius:var(--radius-md);">
                        <table class="custom-table" style="font-size:0.85rem;">
                            <thead>
                                <tr><th>Sem</th><th>Code</th><th>Subject</th><th>Total</th><th>Grade</th><th>Status</th></tr>
                            </thead>
                            <tbody>
                                ${results.length > 0 ? results.map(r => `
                                    <tr>
                                        <td>Sem ${r.semester}</td>
                                        <td><strong>${r.subject_code}</strong></td>
                                        <td>${r.subject_name}</td>
                                        <td>${r.total}/100</td>
                                        <td><span class="badge-custom badge-primary">${r.grade}</span></td>
                                        <td><span class="badge-custom ${r.result_status === 'Pass' ? 'badge-success' : 'badge-danger'}">${r.result_status}</span></td>
                                    </tr>
                                `).join('') : '<tr><td colspan="6" style="text-align:center; color:var(--text-muted);">No examination records.</td></tr>'}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;
        document.getElementById('modal-container').innerHTML = modalHtml;
    } catch (err) {
        UI.showToast('Failed to load profile details: ' + err.message, 'error');
    }
}

function openAddStudentModal() {
    const modalHtml = `
        <div class="modal-backdrop-custom show" id="add-student-modal">
            <div class="modal-content-custom" style="padding: 2rem;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.5rem;">
                    <h4 style="margin:0;"><i class="fas fa-user-plus me-2 text-primary"></i>Add New Student</h4>
                    <button onclick="document.getElementById('add-student-modal').remove()" style="background:none; border:none; font-size:1.25rem; cursor:pointer;"><i class="fas fa-times"></i></button>
                </div>
                <form onsubmit="submitAddStudent(event)">
                    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:0.75rem;">
                        <div class="form-group"><label class="form-label">Student ID</label><input type="text" id="m-stu-id" class="form-control-custom" placeholder="STU101" required></div>
                        <div class="form-group"><label class="form-label">Full Name</label><input type="text" id="m-stu-name" class="form-control-custom" placeholder="John Smith" required></div>
                    </div>
                    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:0.75rem;">
                        <div class="form-group"><label class="form-label">Roll Number</label><input type="text" id="m-stu-roll" class="form-control-custom" placeholder="2026CSE101" required></div>
                        <div class="form-group"><label class="form-label">Registration No.</label><input type="text" id="m-stu-reg" class="form-control-custom" placeholder="REG2026101" required></div>
                    </div>
                    <div class="form-group"><label class="form-label">Email Address</label><input type="email" id="m-stu-email" class="form-control-custom" required></div>
                    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:0.75rem;">
                        <div class="form-group"><label class="form-label">Department</label><select id="m-stu-dept" class="form-control-custom" required>${cachedDepartments.map(d=>`<option value="${d.id}">${d.name}</option>`).join('')}</select></div>
                        <div class="form-group"><label class="form-label">Course</label><select id="m-stu-course" class="form-control-custom" required>${cachedCourses.map(c=>`<option value="${c.id}">${c.name}</option>`).join('')}</select></div>
                    </div>
                    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:0.75rem;">
                        <div class="form-group"><label class="form-label">Semester</label><select id="m-stu-sem" class="form-control-custom"><option value="1">Sem 1</option><option value="2">Sem 2</option><option value="3">Sem 3</option><option value="4">Sem 4</option><option value="5">Sem 5</option><option value="6">Sem 6</option><option value="7">Sem 7</option><option value="8">Sem 8</option></select></div>
                        <div class="form-group"><label class="form-label">Academic Year</label><input type="text" id="m-stu-year" class="form-control-custom" value="2026-2030" required></div>
                    </div>
                    <div class="form-group"><label class="form-label">Login Password (min 8 chars)</label><input type="password" id="m-stu-pwd" class="form-control-custom" placeholder="studentpassword" minlength="8" required></div>
                    <div style="display:flex; justify-content:flex-end; gap:0.75rem; margin-top:1.5rem;">
                        <button type="button" class="btn-secondary-custom" onclick="document.getElementById('add-student-modal').remove()">Cancel</button>
                        <button type="submit" class="btn-primary-custom">Save Student</button>
                    </div>
                </form>
            </div>
        </div>
    `;
    document.getElementById('modal-container').innerHTML = modalHtml;
}

async function submitAddStudent(e) {
    e.preventDefault();
    const payload = {
        student_id: document.getElementById('m-stu-id').value.trim(),
        name: document.getElementById('m-stu-name').value.trim(),
        roll_number: document.getElementById('m-stu-roll').value.trim(),
        registration_number: document.getElementById('m-stu-reg').value.trim(),
        email: document.getElementById('m-stu-email').value.trim(),
        department: document.getElementById('m-stu-dept').value,
        course: document.getElementById('m-stu-course').value,
        semester: document.getElementById('m-stu-sem').value,
        academic_year: document.getElementById('m-stu-year').value,
        password: document.getElementById('m-stu-pwd').value,
    };

    try {
        await API.post('/api/auth/register/', payload);
        UI.showToast('Student added successfully!', 'success');
        document.getElementById('add-student-modal').remove();
        loadStudents();
    } catch (err) {
        UI.showToast(err.message, 'error');
    }
}

async function deleteStudent(studentId, name) {
    if (confirm(`Are you sure you want to delete student "${name}"? This action cannot be undone.`)) {
        try {
            await API.delete(`/api/students/${studentId}/`);
            UI.showToast(`Student ${name} deleted.`, 'info');
            loadStudents();
        } catch (err) {
            UI.showToast('Failed to delete student: ' + err.message, 'error');
        }
    }
}

function exportStudentsExcel() {
    UI.showToast('Preparing student directory spreadsheet...', 'info');
    API.download('/api/students/export-excel/', 'students_directory.xlsx');
}

// ---------------- DEPARTMENTS ----------------
async function loadDepartments() {
    try {
        const depts = await API.get('/api/departments/');
        cachedDepartments = depts;
        const tbody = document.getElementById('depts-tbody');
        tbody.innerHTML = depts.map(d => `
            <tr>
                <td><strong>${d.code}</strong></td>
                <td style="font-weight:700;">${d.name}</td>
                <td><span class="badge-custom badge-primary">${d.student_count || 0} Students</span></td>
                <td style="color:var(--text-secondary); max-width: 350px;">${d.description || '—'}</td>
                <td style="text-align: right;">
                    <button class="action-icon-btn edit" onclick="openEditDeptModal(${d.id})"><i class="fas fa-edit"></i></button>
                    <button class="action-icon-btn delete" onclick="deleteDept(${d.id}, '${d.name}', ${d.student_count || 0})"><i class="fas fa-trash"></i></button>
                </td>
            </tr>
        `).join('');
    } catch (err) {
        UI.showToast('Error loading departments: ' + err.message, 'error');
    }
}

function openAddDeptModal() {
    const modalHtml = `
        <div class="modal-backdrop-custom show" id="dept-modal">
            <div class="modal-content-custom" style="padding: 2rem;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.5rem;">
                    <h4 style="margin:0;"><i class="fas fa-building me-2 text-primary"></i>Add Department</h4>
                    <button onclick="document.getElementById('dept-modal').remove()" style="background:none; border:none; font-size:1.25rem; cursor:pointer;"><i class="fas fa-times"></i></button>
                </div>
                <form onsubmit="submitDept(event)">
                    <div class="form-group"><label class="form-label">Department Code</label><input type="text" id="m-dept-code" class="form-control-custom" placeholder="e.g. CSE" required></div>
                    <div class="form-group"><label class="form-label">Department Name</label><input type="text" id="m-dept-name" class="form-control-custom" placeholder="e.g. Computer Science & Engineering" required></div>
                    <div class="form-group"><label class="form-label">Description</label><textarea id="m-dept-desc" class="form-control-custom" rows="3"></textarea></div>
                    <div style="display:flex; justify-content:flex-end; gap:0.75rem; margin-top:1.5rem;">
                        <button type="button" class="btn-secondary-custom" onclick="document.getElementById('dept-modal').remove()">Cancel</button>
                        <button type="submit" class="btn-primary-custom">Save Department</button>
                    </div>
                </form>
            </div>
        </div>
    `;
    document.getElementById('modal-container').innerHTML = modalHtml;
}

async function submitDept(e) {
    e.preventDefault();
    const payload = {
        code: document.getElementById('m-dept-code').value.trim(),
        name: document.getElementById('m-dept-name').value.trim(),
        description: document.getElementById('m-dept-desc').value.trim()
    };
    try {
        await API.post('/api/departments/', payload);
        UI.showToast('Department added!', 'success');
        document.getElementById('dept-modal').remove();
        loadDepartments();
    } catch (err) {
        UI.showToast(err.message, 'error');
    }
}

async function deleteDept(deptId, name, studentCount) {
    if (studentCount > 0) {
        UI.showToast(`Cannot delete "${name}" because it contains ${studentCount} active students.`, 'error');
        return;
    }
    if (confirm(`Delete department "${name}"?`)) {
        try {
            await API.delete(`/api/departments/${deptId}/`);
            UI.showToast('Department deleted.', 'info');
            loadDepartments();
        } catch (err) {
            UI.showToast(err.message, 'error');
        }
    }
}

// ---------------- COURSES ----------------
async function loadCourses() {
    try {
        const courses = await API.get('/api/courses/');
        cachedCourses = courses;
        const tbody = document.getElementById('courses-tbody');
        tbody.innerHTML = courses.map(c => `
            <tr>
                <td><strong>${c.code}</strong></td>
                <td style="font-weight:700;">${c.name}</td>
                <td><span class="badge-custom badge-warning">${c.duration}</span></td>
                <td><span class="badge-custom badge-primary">${c.student_count || 0} Students</span></td>
                <td style="color:var(--text-secondary);">${c.description || '—'}</td>
                <td style="text-align: right;">
                    <button class="action-icon-btn delete" onclick="deleteCourse(${c.id}, '${c.name}', ${c.student_count || 0})"><i class="fas fa-trash"></i></button>
                </td>
            </tr>
        `).join('');
    } catch (err) {
        UI.showToast('Error loading courses: ' + err.message, 'error');
    }
}

function openAddCourseModal() {
    const modalHtml = `
        <div class="modal-backdrop-custom show" id="course-modal">
            <div class="modal-content-custom" style="padding: 2rem;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.5rem;">
                    <h4 style="margin:0;"><i class="fas fa-book me-2 text-primary"></i>Add Course</h4>
                    <button onclick="document.getElementById('course-modal').remove()" style="background:none; border:none; font-size:1.25rem; cursor:pointer;"><i class="fas fa-times"></i></button>
                </div>
                <form onsubmit="submitCourse(event)">
                    <div class="form-group"><label class="form-label">Course Code</label><input type="text" id="m-crs-code" class="form-control-custom" placeholder="e.g. BTECH" required></div>
                    <div class="form-group"><label class="form-label">Course Title</label><input type="text" id="m-crs-name" class="form-control-custom" placeholder="e.g. Bachelor of Technology" required></div>
                    <div class="form-group"><label class="form-label">Duration</label><input type="text" id="m-crs-dur" class="form-control-custom" placeholder="e.g. 4 Years" required></div>
                    <div class="form-group"><label class="form-label">Description</label><textarea id="m-crs-desc" class="form-control-custom" rows="2"></textarea></div>
                    <div style="display:flex; justify-content:flex-end; gap:0.75rem; margin-top:1.5rem;">
                        <button type="button" class="btn-secondary-custom" onclick="document.getElementById('course-modal').remove()">Cancel</button>
                        <button type="submit" class="btn-primary-custom">Save Course</button>
                    </div>
                </form>
            </div>
        </div>
    `;
    document.getElementById('modal-container').innerHTML = modalHtml;
}

async function submitCourse(e) {
    e.preventDefault();
    const payload = {
        code: document.getElementById('m-crs-code').value.trim(),
        name: document.getElementById('m-crs-name').value.trim(),
        duration: document.getElementById('m-crs-dur').value.trim(),
        description: document.getElementById('m-crs-desc').value.trim()
    };
    try {
        await API.post('/api/courses/', payload);
        UI.showToast('Course added!', 'success');
        document.getElementById('course-modal').remove();
        loadCourses();
    } catch (err) {
        UI.showToast(err.message, 'error');
    }
}

async function deleteCourse(courseId, name, studentCount) {
    if (studentCount > 0) {
        UI.showToast(`Cannot delete "${name}" because it contains enrolled students.`, 'error');
        return;
    }
    if (confirm(`Delete course "${name}"?`)) {
        try {
            await API.delete(`/api/courses/${courseId}/`);
            UI.showToast('Course deleted.', 'info');
            loadCourses();
        } catch (err) {
            UI.showToast(err.message, 'error');
        }
    }
}

// ---------------- RESULTS ----------------
async function loadResults() {
    const query = document.getElementById('result-search-input')?.value.trim();
    const sem = document.getElementById('result-filter-sem')?.value;

    try {
        const results = await API.get('/api/results/', { q: query, semester: sem });
        const tbody = document.getElementById('results-tbody');

        if (results.length === 0) {
            tbody.innerHTML = '<tr><td colspan="9" style="text-align:center; padding: 2rem; color:var(--text-muted);"><i class="fas fa-search me-2"></i>No semester result records found.</td></tr>';
            return;
        }

        tbody.innerHTML = results.map(r => `
            <tr>
                <td>
                    <div style="font-weight:700;">${r.student_name}</div>
                    <div style="font-size:0.8rem; color:var(--text-muted);">${r.student_roll}</div>
                </td>
                <td><span class="badge-custom badge-warning">Sem ${r.semester}</span></td>
                <td><strong>${r.subject_code}</strong></td>
                <td>${r.subject_name}</td>
                <td>${r.internal_marks} + ${r.external_marks}</td>
                <td style="font-weight:700;">${r.total} / 100</td>
                <td><span class="badge-custom badge-primary">${r.grade}</span></td>
                <td><span class="badge-custom ${r.result_status === 'Pass' ? 'badge-success' : 'badge-danger'}">${r.result_status}</span></td>
                <td style="text-align: right;">
                    <button class="action-icon-btn delete" onclick="deleteResult(${r.id})"><i class="fas fa-trash"></i></button>
                </td>
            </tr>
        `).join('');
    } catch (err) {
        UI.showToast('Error loading results: ' + err.message, 'error');
    }
}

async function openAddResultModal() {
    if (cachedStudents.length === 0) {
        cachedStudents = await API.get('/api/students/');
    }

    const modalHtml = `
        <div class="modal-backdrop-custom show" id="result-modal">
            <div class="modal-content-custom" style="padding: 2rem;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.5rem;">
                    <h4 style="margin:0;"><i class="fas fa-award me-2 text-primary"></i>Publish Semester Result</h4>
                    <button onclick="document.getElementById('result-modal').remove()" style="background:none; border:none; font-size:1.25rem; cursor:pointer;"><i class="fas fa-times"></i></button>
                </div>
                <form onsubmit="submitResult(event)">
                    <div class="form-group">
                        <label class="form-label">Student</label>
                        <select id="m-res-stu" class="form-control-custom" required>
                            ${cachedStudents.map(s=>`<option value="${s.id}">${s.name} (${s.roll_number})</option>`).join('')}
                        </select>
                    </div>
                    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:0.75rem;">
                        <div class="form-group">
                            <label class="form-label">Semester</label>
                            <select id="m-res-sem" class="form-control-custom" required>
                                <option value="1">Sem 1</option><option value="2">Sem 2</option><option value="3">Sem 3</option><option value="4">Sem 4</option>
                                <option value="5">Sem 5</option><option value="6">Sem 6</option><option value="7">Sem 7</option><option value="8">Sem 8</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Credits</label>
                            <input type="number" id="m-res-cred" class="form-control-custom" value="4" min="1" max="6" required>
                        </div>
                    </div>
                    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:0.75rem;">
                        <div class="form-group">
                            <label class="form-label">Subject Code</label>
                            <input type="text" id="m-res-code" class="form-control-custom" placeholder="CS-501" required>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Subject Title</label>
                            <input type="text" id="m-res-name" class="form-control-custom" placeholder="Operating Systems" required>
                        </div>
                    </div>
                    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:0.75rem;">
                        <div class="form-group">
                            <label class="form-label">Internal Marks (max 30/40)</label>
                            <input type="number" step="0.5" id="m-res-int" class="form-control-custom" placeholder="28.5" max="100" required>
                        </div>
                        <div class="form-group">
                            <label class="form-label">External Marks (max 70/60)</label>
                            <input type="number" step="0.5" id="m-res-ext" class="form-control-custom" placeholder="62.0" max="100" required>
                        </div>
                    </div>
                    <div style="display:flex; justify-content:flex-end; gap:0.75rem; margin-top:1.5rem;">
                        <button type="button" class="btn-secondary-custom" onclick="document.getElementById('result-modal').remove()">Cancel</button>
                        <button type="submit" class="btn-primary-custom">Publish Result</button>
                    </div>
                </form>
            </div>
        </div>
    `;
    document.getElementById('modal-container').innerHTML = modalHtml;
}

async function submitResult(e) {
    e.preventDefault();
    const payload = {
        student: document.getElementById('m-res-stu').value,
        semester: parseInt(document.getElementById('m-res-sem').value),
        credit: parseInt(document.getElementById('m-res-cred').value),
        subject_code: document.getElementById('m-res-code').value.trim(),
        subject_name: document.getElementById('m-res-name').value.trim(),
        internal_marks: parseFloat(document.getElementById('m-res-int').value),
        external_marks: parseFloat(document.getElementById('m-res-ext').value)
    };

    try {
        await API.post('/api/results/', payload);
        UI.showToast('Result published and GPA updated!', 'success');
        document.getElementById('result-modal').remove();
        loadResults();
    } catch (err) {
        UI.showToast(err.message, 'error');
    }
}

async function deleteResult(resultId) {
    if (confirm('Delete this examination result record? GPA metrics will automatically recalculate.')) {
        try {
            await API.delete(`/api/results/${resultId}/`);
            UI.showToast('Record deleted.', 'info');
            loadResults();
        } catch (err) {
            UI.showToast(err.message, 'error');
        }
    }
}

// Initial Boot
document.addEventListener('DOMContentLoaded', () => {
    loadDashboard();
});
