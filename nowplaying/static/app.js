const API_URL = '/now-playing';
const colorThief = new ColorThief();


async function updateDashboard() {
    try {
        const response = await fetch(API_URL);
        const data = await response.json();

        const titleEl = document.getElementById('track-title');
        const artistEl = document.getElementById('track-artist');
        const artEl = document.getElementById('album-art');
        const badgeEl = document.getElementById('status-badge');
        const bodyEl = document.body;
        let color = "#0b0f19";
        // Actualizar textos
        titleEl.textContent = data.title;
        artistEl.textContent = data.artist;

        // Gestionar la carátula de la canción
        if (data.success && data.album_art) {
            
            // 1. Si la canción es nueva, configuramos todo ANTES de cambiar el src
            if (artEl.src !== data.album_art) {
                artEl.style.opacity = "0";
                
                setTimeout(() => {
                    artEl.crossOrigin = "Anonymous";
                    
                    // B. Programamos que vuelva a aparecer cuando la NUEVA esté completamente lista
                    artEl.onload = function() {
                        try {
                            const rgb = colorThief.getColor(artEl);
                            const factor = 0.4; 
                            const rOscuro = Math.floor(rgb[0] * factor);
                            const gOscuro = Math.floor(rgb[1] * factor);
                            const bOscuro = Math.floor(rgb[2] * factor);
                            
                            bodyEl.style.backgroundColor = `rgb(${rOscuro}, ${gOscuro}, ${bOscuro})`;
                        } catch (e) {
                            console.error("Error en ColorThief al cargar:", e);
                            bodyEl.style.backgroundColor = "#0b0f19";
                        }
                        
                        // C. ¡Aparece la nueva carátula suavemente!
                        artEl.style.opacity = "1";
                    };
                    
                    // Cambiamos el src real que dispara el onload de arriba
                    artEl.src = data.album_art;
                    
                }, 200);
            }

            badgeEl.textContent = "Now Playing";
            badgeEl.className = "status-badge"; 

        } else {
            // 2. Quitamos el CORS antes de meter una imagen genérica o local
            artEl.removeAttribute('crossOrigin');
            
            // 3. Imagen por defecto (Usamos un SVG integrado en texto para que NUNCA falle, no dependa de internet y cargue al instante)
            const defaultImg = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%239ca3af'><path d='M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z'/></svg>";
            
            if (artEl.src !== defaultImg) {
                artEl.src = defaultImg;
            }

            // 4. Forzamos que el fondo vuelva a su azul oscuro original inmediatamente
            bodyEl.style.transition = "background-color 1s ease";
            bodyEl.style.backgroundColor = "#0b0f19";
            badgeEl.textContent = "Nothing Playing";

        }


    } catch (error) {
        console.error('Error al conectar con la API:', error);
        document.getElementById('status-badge').textContent = "Connection Error";
    }
}

// Preguntar a la API cada 3 segundos
setInterval(updateDashboard, 3000);

// Ejecutar una vez al cargar la página para no esperar los primeros 3 segundos
updateDashboard();
