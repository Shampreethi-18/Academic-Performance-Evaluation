document.addEventListener("DOMContentLoaded", () => {
    loadStudents();
    loadStats();
    loadChart();
});

/* ================= ADD ATTENDANCE ================= */
function addAttendance(event) {
    event.preventDefault();
    const register_no = document.getElementById("register_no").value.trim();
    const name = document.getElementById("name").value.trim();
    const subject = document.getElementById("subject").value.trim();
    const attended = document.getElementById("attended").value;
    const total = document.getElementById("total").value;

    if (!register_no || !name || !subject || attended === "" || total === "") {
        alert("Please fill all fields");
        return;
    }

    fetch("/add", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            register_no,
            name,
            subject,
            attended: Number(attended),
            total: Number(total)
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            ["register_no","name","subject","attended","total"]
                .forEach(id => document.getElementById(id).value = "");

            loadStudents();
            loadStats();
            loadChart();
        } else {
            alert(data.error);
        }
    });
}

/* ================= LOAD STUDENTS ================= */
function loadStudents() {
    fetch("/students")
        .then(res => res.json())
        .then(data => {
            const table = document.getElementById("student-table");
            table.innerHTML = "";

            data.forEach(s => {
                table.innerHTML += `
                <tr>
                    <td>${s.register_no}</td>
                    <td>${s.name}</td>
                    <td>${s.subject}</td>
                    <td>${s.percentage}%</td>
                    <td class="${s.risk === 'High' ? 'high-risk' : 'safe'}">${s.risk}</td>
                    <td>
                        <button onclick="deleteStudent(${s.id})">Delete</button>
                    </td>
                </tr>`;
            });
        });
}

/* ================= STATS ================= */
function loadStats() {
    fetch("/stats")
        .then(res => res.json())
        .then(d => {
            document.getElementById("totalStudents").innerText = d.total;
            document.getElementById("avgAttendance").innerText = d.average + "%";
            document.getElementById("highRisk").innerText = d.high_risk;
        });
}

/* ================= DELETE ================= */
function deleteStudent(id) {
    if (!confirm("Delete this record?")) return;

    fetch(`/delete/${id}`, { method: "POST" })
        .then(() => {
            loadStudents();
            loadStats();
            loadChart();
        });
}

/* ================= CHART ================= */
let attendanceChart = null;

function loadChart() {
    fetch("/students")
        .then(res => res.json())
        .then(data => {
            const labels = data.map(s => `${s.name} (${s.subject})`);
            const values = data.map(s => s.percentage);

            const ctx = document.getElementById("attendanceChart");

            if (attendanceChart) attendanceChart.destroy();

            attendanceChart = new Chart(ctx, {
                type: "bar",
                data: {
                    labels,
                    datasets: [{
                        label: "Attendance %",
                        data: values
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: { beginAtZero: true, max: 100 }
                    }
                }
            });
        });
}
