// static/js/main.js
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips de Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Funcionalidad de filtrado en la página de destinos
    const filterButtons = document.querySelectorAll('.filter-btn');
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            const filter = this.getAttribute('data-filter');
            filterDestinations(filter);
            
            // Actualizar estado activo de los botones
            filterButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
        });
    });
});

// Función para filtrar destinos
function filterDestinations(category) {
    const cards = document.querySelectorAll('.destination-card');
    cards.forEach(card => {
        if (category === 'all' || card.getAttribute('data-category') === category) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

// Funciones para la página de reservas
function updatePrice() {
    const startDateInput = document.getElementById('start_date');
    const endDateInput = document.getElementById('end_date');
    const passengersInput = document.getElementById('passengers');
    
    if (!startDateInput || !endDateInput || !passengersInput) return;
    
    const startDate = new Date(startDateInput.value);
    const endDate = new Date(endDateInput.value);
    const passengers = parseInt(passengersInput.value);
    const pricePerPerson = parseFloat(document.getElementById('price-per-person').innerText.replace('$', ''));
    
    if (startDate && endDate && !isNaN(startDate) && !isNaN(endDate)) {
        // Calcular la diferencia en días
        const timeDiff = endDate - startDate;
        const nights = Math.ceil(timeDiff / (1000 * 60 * 60 * 24));
        
        if (nights > 0) {
            document.getElementById('total-nights').innerText = nights;
            document.getElementById('total-passengers').innerText = passengers;
            const totalPrice = pricePerPerson * passengers * nights;
            document.getElementById('total-price').innerText = '$' + totalPrice.toFixed(2);
        } else {
            document.getElementById('total-nights').innerText = '0';
            document.getElementById('total-price').innerText = '$0.00';
        }
    }
}

// Agregar event listeners para los campos de fecha
document.addEventListener('DOMContentLoaded', function() {
    const startDateInput = document.getElementById('start_date');
    const endDateInput = document.getElementById('end_date');
    const passengersInput = document.getElementById('passengers');
    
    if (startDateInput && endDateInput && passengersInput) {
        startDateInput.addEventListener('change', updatePrice);
        endDateInput.addEventListener('change', updatePrice);
        passengersInput.addEventListener('change', updatePrice);
        
        // Establecer la fecha mínima como hoy
        const today = new Date().toISOString().split('T')[0];
        startDateInput.min = today;
        endDateInput.min = today;
    }
});

// Funcionalidad de búsqueda en tiempo real
let searchTimeout;
document.querySelector('input[name="q"]')?.addEventListener('input', function(e) {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        const query = e.target.value;
        if (query.length >= 3) {
            searchDestinations(query);
        }
    }, 500);
});

// Función para búsqueda AJAX
function searchDestinations(query) {
    fetch(`/search?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            updateDestinationsList(data);
        })
        .catch(error => console.error('Error:', error));
}

// Actualizar lista de destinos con resultados de búsqueda
function updateDestinationsList(results) {
    const container = document.getElementById('destinations-container');
    if (!container) return;

    container.innerHTML = results.map(destination => `
        <div class="col">
            <div class="card h-100 shadow-sm">
                <img src="${destination.image_url}" class="card-img-top" alt="${destination.name}">
                <div class="card-body">
                    <h5 class="card-title">${destination.name}</h5>
                    <p class="card-text">${destination.description}</p>
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="price-tag">$${destination.price}</span>
                        <div class="btn-group">
                            <a href="/destination/${destination.id}" class="btn btn-sm btn-outline-secondary">Ver detalles</a>
                            <a href="/booking/${destination.id}" class="btn btn-sm btn-primary">Reservar</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}