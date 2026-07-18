document.getElementById('vin-form').addEventListener('submit', async function (event) {
    event.preventDefault();
    const vin = document.getElementById('vin').value;

    const response = await fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ vin })
    });

    const result = await response.json();
    document.getElementById('result').innerText = JSON.stringify(result, null, 2);
});