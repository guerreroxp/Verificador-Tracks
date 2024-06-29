import tkinter as tk
from tkinter import filedialog, messagebox
import gpxpy
from fpdf import FPDF
from geopy.distance import distance

class GPSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Verificador de Ruta GPS")
        self.root.geometry("800x600")

        self.route_file = ""
        self.track_file = ""
        self.proximity_radius = 50
        self.missed_waypoint_penalty = 15
        self.cp_waypoint_penalty = 120

        self.create_widgets()

    def create_widgets(self):
        self.settings_frame = tk.Frame(self.root)
        self.settings_frame.pack(pady=10)

        self.radius_label = tk.Label(self.settings_frame, text="Radio de Proximidad (metros):")
        self.radius_label.pack(side=tk.LEFT, padx=5)

        self.radius_entry = tk.Entry(self.settings_frame)
        self.radius_entry.insert(0, str(self.proximity_radius))
        self.radius_entry.pack(side=tk.LEFT, padx=5)

        self.missed_time_label = tk.Label(self.settings_frame, text="Penalización por Punto Perdido (minutos):")
        self.missed_time_label.pack(side=tk.LEFT, padx=5)

        self.missed_time_entry = tk.Entry(self.settings_frame)
        self.missed_time_entry.insert(0, str(self.missed_waypoint_penalty))
        self.missed_time_entry.pack(side=tk.LEFT, padx=5)

        self.cp_time_label = tk.Label(self.settings_frame, text="Penalización por Punto de Control (minutos):")
        self.cp_time_label.pack(side=tk.LEFT, padx=5)

        self.cp_time_entry = tk.Entry(self.settings_frame)
        self.cp_time_entry.insert(0, str(self.cp_waypoint_penalty))
        self.cp_time_entry.pack(side=tk.LEFT, padx=5)

        self.set_radius_button = tk.Button(self.settings_frame, text="Configurar Valores", command=self.set_values)
        self.set_radius_button.pack(side=tk.LEFT, padx=5)

        self.load_route_button = tk.Button(self.root, text="Cargar Ruta GPX", command=self.load_route)
        self.load_route_button.pack(pady=10)

        self.load_track_button = tk.Button(self.root, text="Cargar Track GPX", command=self.load_track)
        self.load_track_button.pack(pady=10)

        self.check_button = tk.Button(self.root, text="Verificar Proximidad", command=self.check_proximity)
        self.check_button.pack(pady=10)

        self.export_pdf_button = tk.Button(self.root, text="Exportar a PDF", command=self.export_to_pdf)
        self.export_pdf_button.pack(pady=10)

        self.results_text = tk.Text(self.root, height=20, width=70)
        self.results_text.pack(pady=10)

        self.time_penalty_label = tk.Label(self.root, text="", fg="red", font=("Arial", 12, "bold"))
        self.time_penalty_label.pack(pady=5)

    def set_values(self):
        try:
            self.proximity_radius = float(self.radius_entry.get())
            self.missed_waypoint_penalty = int(self.missed_time_entry.get())
            self.cp_waypoint_penalty = int(self.cp_time_entry.get())
            messagebox.showinfo("Valores Configurados", f"Radio de proximidad configurado a {self.proximity_radius} metros.\n"
                                                          f"Penalización por punto perdido configurada a {self.missed_waypoint_penalty} minutos.\n"
                                                          f"Penalización por punto de control configurada a {self.cp_waypoint_penalty} minutos.")
        except ValueError:
            messagebox.showerror("Entrada Inválida", "Por favor ingrese números válidos para el radio y las penalizaciones.")

    def load_route(self):
        self.route_file = filedialog.askopenfilename(filetypes=[("Archivos GPX", "*.gpx")])
        if self.route_file:
            messagebox.showinfo("Archivo Cargado", f"Ruta GPX cargada: {self.route_file}")

    def load_track(self):
        self.track_file = filedialog.askopenfilename(filetypes=[("Archivos GPX", "*.gpx")])
        if self.track_file:
            messagebox.showinfo("Archivo Cargado", f"Track GPX cargado: {self.track_file}")

    def read_gpx(self, file_path):
        with open(file_path, 'r', encoding="utf-8") as gpx_file:
            gpx = gpxpy.parse(gpx_file)
        waypoints = [(wpt.name, wpt.latitude, wpt.longitude, wpt.comment) for wpt in gpx.waypoints]
        trackpoints = [(point.latitude, point.longitude) for track in gpx.tracks for segment in track.segments for point in segment.points]
        return waypoints, trackpoints

    def check_proximity(self):
        if not self.route_file or not self.track_file:
            messagebox.showwarning("Archivos Faltantes", "Por favor cargue tanto el archivo de ruta como el archivo de track GPX.")
            return

        route_waypoints, _ = self.read_gpx(self.route_file)
        _, track_trackpoints = self.read_gpx(self.track_file)

        self.results_text.delete('1.0', tk.END)
        total_time_penalty = 0

        for name, lat, lon, comment in route_waypoints:
            wp_result = {'name': name, 'coordinates': (lat, lon), 'status': 'no_pass', 'min_distance': float('inf')}
            for trackpoint in track_trackpoints:
                dist = distance((lat, lon), trackpoint).meters
                if dist <= self.proximity_radius:
                    wp_result['status'] = 'pass'
                    wp_result['min_distance'] = 0
                    break
                if dist < wp_result['min_distance']:
                    wp_result['min_distance'] = dist

            result_text = f"Punto de Ruta {wp_result['name']} ({wp_result['coordinates']}) - Estado: {wp_result['status']} - Distancia Mínima: {wp_result['min_distance']:.2f} metros\n"
            if wp_result['status'] == 'no_pass':
                if comment == 'cp':
                    total_time_penalty += self.cp_waypoint_penalty
                else:
                    total_time_penalty += self.missed_waypoint_penalty
                self.results_text.insert(tk.END, result_text, 'fail')
            else:
                self.results_text.insert(tk.END, result_text)

        self.results_text.tag_config('fail', foreground='red')
        self.update_time_penalty_label(total_time_penalty)

    def update_time_penalty_label(self, penalty):
        self.time_penalty_label.config(text=f"Total de Penalización de Tiempo: {penalty} minutos")

    def export_to_pdf(self):
        if not self.route_file or not self.track_file:
            messagebox.showwarning("Archivos Faltantes", "Por favor cargue tanto el archivo de ruta como el archivo de track GPX.")
            return

        route_name = self.get_route_name()
        pilot_name = self.get_pilot_name()
        total_penalty = self.time_penalty_label.cget("text")

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", size=10)

        pdf.cell(200, 10, txt=f"INFORME - Etapa - {route_name}", ln=True, align='C')

        for line in self.results_text.get('1.0', tk.END).splitlines():
            if 'no_pass' in line:
                pdf.set_text_color(255, 0, 0)
            pdf.multi_cell(0, 10, line)
            pdf.set_text_color(0, 0, 0)

        pdf.set_text_color(0, 128, 0)  # Cambiamos a verde
        pdf.set_font("Arial", size=12, style='B')
        pdf.multi_cell(0, 10, f"Piloto: {pilot_name}", align='L')
        pdf.set_text_color(0, 0, 0)

        pdf.multi_cell(0, 10, f"Advertencia: {total_penalty}", align='L')

        pdf.multi_cell(0, 10, f"\n\nCreado por @Ecooempresas", align='L')

        pdf_file = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("Archivos PDF", "*.pdf")])
        if pdf_file:
            pdf.output(pdf_file)

    def get_route_name(self):
        if self.route_file:
            return f"Ruta {self.route_file.split('/')[-1].split('.')[0]}"
        return ""

    def get_pilot_name(self):
        if self.track_file:
            with open(self.track_file, 'r', encoding="utf-8") as track_file:
                track_data = track_file.read()
                start_index = track_data.find('<name>') + len('<name>')
                end_index = track_data.find('</name>')
                return f"{track_data[start_index:end_index].strip()}"

if __name__ == "__main__":
    root = tk.Tk()
    app = GPSApp(root)
    root.mainloop()
