// toggle virtual/physical sessions
function toggleLocationType(type) {
    document.getElementById('virtual-section').style.display = type === 'virtual' ? 'block' : 'none';
    document.getElementById('physical-section').style.display = type === 'physical' ? 'block' : 'none';
}

// smart suggestion buttons
document.querySelectorAll('.suggestion-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const datetime = this.dataset.datetime;
        document.querySelector('[name="scheduled_date"]').value = datetime;
        // trigger conflict check
        checkConflict(datetime);
        // highlight selected
        document.querySelectorAll('.suggestion-btn').forEach(b => b.classList.remove('btn-primary'));
        this.classList.remove('btn-outline-primary');
        this.classList.add('btn-primary');
    });
});

// realt time conflict checking
let conflictTimer;
document.querySelector('[name="scheduled_date"]').addEventListener('change', function() {
    clearTimeout(conflictTimer);
    conflictTimer = setTimeout(() => checkConflict(thid.value), 500);
});

function checkConflict(datetimeValue) {
    if (!datetimeValue) return;

    const timezone = document.querySelector('[name="timezone"]').value;
    const duration = document.querySelector('[name="duration_minutes"]').value;

    fetch('{% url "scheduling:api_check_conflict" %}', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}',
        },
        body: JSON.stringify({
            datetime: datetimeValue,
            duration: duration,
            timezone: timezone,
        })
    })
    .then(r => r.json())
    .then(data => {
        const warning = document.getElementById('conflic-warning');
        const ok = document.getElementById('conflict-ok');

        if (data.has_conflict) {
            warning.textContent = '⚠️' + data.message;
            warning.style.display = 'block';
            ok.style.display = 'none';
        } else {
            ok.style.display = 'block';
            warning.style.display = 'none';
        }
    })
    .catch(console.error);
}