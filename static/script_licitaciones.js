function validateImportes() {
    let errorMessageImportes = document.getElementById("error-message-importes");
    let errorMessageFechas = document.getElementById("error-message-fechas");

    // Validación de importes
    let importe1 = document.getElementById("importe1").value.replace(/\./g, ""); // Elimina puntos (formateo previo)
    let importe2 = document.getElementById("importe2").value.replace(/\./g, ""); // Elimina puntos (formateo previo)
    importe1 = parseInt(importe1, 10); // Convierte el valor a entero
    importe2 = parseInt(importe2, 10); // Convierte el valor a entero

    // Comprueba si el importe mínimo es mayor que el importe máximo
    if (importe1 > importe2) {
        errorMessageImportes.textContent = "El importe mínimo no puede ser mayor que el importe máximo.";
        errorMessageImportes.style.display = "block"; // Muestra el mensaje de error
        return false; // Retorna falso para indicar que la validación falló
    } else {
        errorMessageImportes.style.display = "none"; // Oculta el mensaje de error si la validación pasa
    }

    // Validación de fechas
    let fecha1 = document.getElementById("fecha1").value;
    let fecha2 = document.getElementById("fecha2").value;

    // Comprueba si la fecha mínima es mayor que la fecha máxima
    if (fecha1 && fecha2 && fecha1 > fecha2) {
        errorMessageFechas.textContent = "La fecha mínima no puede ser mayor que la fecha máxima.";
        errorMessageFechas.style.display = "block"; // Muestra el mensaje de error
        return false; // Retorna falso para indicar que la validación falló
    } else {
        errorMessageFechas.style.display = "none"; // Oculta el mensaje de error si la validación pasa
    }
}

document.addEventListener("DOMContentLoaded", function () {
    // Para el campo importe1
    const input1 = document.getElementById("importe1");
    input1.addEventListener("input", function () {
        let value = input1.value.replace(/\D/g, ""); // Elimina caracteres no numéricos
        let cursorPosition = input1.selectionStart; // Guarda la posición del cursor antes del cambio

        // Formatear número con puntos cada tres dígitos
        let formattedValue = new Intl.NumberFormat("de-DE").format(value);
        input1.value = formattedValue; // Asigna el valor formateado

        // Ajustar la posición del cursor después de formatear
        let diff = input1.value.length - value.length;
        input1.setSelectionRange(cursorPosition + diff, cursorPosition + diff);
    });

    // Para el campo importe2
    const input2 = document.getElementById("importe2");
    input2.addEventListener("input", function () {
        let value = input2.value.replace(/\D/g, ""); // Elimina caracteres no numéricos
        let cursorPosition = input2.selectionStart; // Guarda la posición del cursor antes del cambio

        // Formatear número con puntos cada tres dígitos
        let formattedValue = new Intl.NumberFormat("de-DE").format(value);
        input2.value = formattedValue; // Asigna el valor formateado

        // Ajustar la posición del cursor después de formatear
        let diff = input2.value.length - value.length;
        input2.setSelectionRange(cursorPosition + diff, cursorPosition + diff);
    });
});

async function limpiarCampos() {
    // Vaciar todos los campos del formulario
    document.querySelectorAll("input, textarea, select").forEach(campo => {
        if (campo.type === "text" || campo.type === "number" || campo.type === "date") {
            campo.value = ""; // Limpiar campos de texto, números y fechas
        } else if (campo.type === "select-one") {
            campo.selectedIndex = 0; // Restablecer selects al primer elemento
        }
    });

    // Enviar solicitud al servidor para limpiar la sesión
    try {
        await fetch('/limpiar-sesion', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        console.log("Sesión limpiada.");
    } catch (error) {
        console.error("Error al limpiar la sesión:", error);
    }
}

function scrollToTop() {
            window.scrollTo({
                top: 0, // Desplazar hasta la parte superior
                behavior: 'smooth' // Scroll suave
            });
        }