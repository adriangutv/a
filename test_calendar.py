from utils.calendar import agendar_google_meet

if __name__ == "__main__":
    nombre = "Adrián Gutiérrez"
    correo = "adrian.g@bpse-truck.com"  # Cambia por un correo real para que le llegue invitación
    fecha_iso = "2025-06-05T17:00:00"  # Horario de CDMX (UTC-6)

    resultado = agendar_google_meet(nombre, correo, fecha_iso)
    print(resultado)

