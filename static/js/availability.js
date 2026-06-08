// detect browser timezone
const detectedTz = Intl.DateTimeFormat().resolvedOptions().timeZone;
document.getElementById('detected-tz').textContent = detectedTz;

function applyDetectedTimezone(){
    const select = document.querySelector('[name="timezone]');
    if (select) {
        // find the matching option
        for (let option of select.options) {
            if (option.value === detectedTz) {
                option.selected = true;
                break;
            }
        }
    }
}

// preset slot buttons
document.querySelectorAll('.preset-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const day = this.dataset.day;
        const start = this.dataset.start;
        const end = this.dataset.end;

        // fill the add availability slot form
        document.querySelector('[name="day_of_week"]').value = day;
        document.querySelector('[name="start_time"]').value = start;
        document.querySelector('[name="end_time"]').value = end;

        // highlight the form to show it has been filled
        document.querySelector('[name="start_time]')
            .closest('.card').scrollIntoView({ 
                behavior: 'smooth' 
        });
    });
});

// add all weekdays
function addWeekdays() {
    const days = [
        { day: 0, start: '09:00', end: '17:00' },
        { day: 1, start: '09:00', end: '17:00' },
        { day: 2, start: '09:00', end: '17:00' },
        { day: 3, start: '09:00', end: '17:00' },
        { day: 4, start: '09:00', end: '17:00' },
    ];

    // submit eac day as a separste form post vias fetch
    const csrfToken = document.querySelector('[name="csrfmiddlewaretoken"]').value;
    const promises = days.map(d => 
        fetch(window.location.href, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: new URLSearchParams({
                csrfmiddlewaretoken: csrfToken,
                action: 'add_slot',
                day_of_week: d.day,
                start_time: d.start,
                end_time: d.end,
            })
        })
    );

    Promise.all(promise).then(() => {
        window.location.reload();
    });
}