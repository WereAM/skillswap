// week navigation
function navigateWeek(direction) {
    const url = new URL(window.location);
    const current = parseInt(url.searchParams.get('week') || 0);
    url.searchParams.set('week', current + direction);
    window.location = url;
}

// position the session blocks precisely on the grid
document.addEventListener('DOMContentLoaded', function() {
    const grid = document.querySelector('.calendar-grid');
    if (!grid) return;

    const gridRect = grid.getBoundingClientRect();
    const headerHeight = 60; // px
    const hourHeight = 72; // px per hour row
    const startHour = 0; // 12am
    const gutterWidth = 56 // px
    const colWidth = (grid.offsetWidth - gutterWidth) / 7; //

    document.querySelectorAll('.session-block').forEach(block => {
        const day = parseInt(block.dataset.day);
        const hour = parseInt(block.dataset.hour);
        const minute = parseInt(block.dataset.minute);
        const duration = parseInt(block.dataset.duration);

        const top = (hour * hourHeight) + ((minute / 60) * hourHeight) + 4;
        const left = (day * colWidth) + 4; // 4px padding
        const height = Math.max(((duration / 60) * hourHeight) - 8, 24);
        const width = colWidth - 8;

        block.style.position = 'absolute';
        block.style.top = top + 'px';
        block.style.left = left + 'px'
        block.style.height = height + 'px'
        block.style.width = width + 'px'
    });
});