const points = window.WEATHER_DATA || [];
const ctx = document.getElementById('weatherChart');

if (ctx && points.length) {
    new Chart(ctx, {
        data: {
            labels: points.map(x => x.time),
            datasets: [
                {
                    type: 'line',
                    label: 'Temperature °C',
                    data: points.map(x => x.temperature),
                    borderWidth: 3,
                    tension: 0.35,
                    yAxisID: 'temp'
                },
                {
                    type: 'bar',
                    label: 'Rain chance %',
                    data: points.map(x => x.probability),
                    borderWidth: 0,
                    borderRadius: 5,
                    yAxisID: 'rain'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                legend: { labels: { color: '#b8c3d6' } }
            },
            scales: {
                x: { ticks: { color: '#8491a7', maxTicksLimit: 8 }, grid: { display: false } },
                temp: { position: 'left', ticks: { color: '#8491a7' }, grid: { color: 'rgba(255,255,255,.06)' } },
                rain: { position: 'right', min: 0, max: 100, ticks: { color: '#8491a7' }, grid: { display: false } }
            }
        }
    });
}
