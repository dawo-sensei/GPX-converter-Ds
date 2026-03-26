import os
import sys
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import xml.etree.ElementTree as ET

def kml_to_gpx(kml_file, gpx_file):
    """
    Converts a .kml file to a .gpx file.
    """
    try:
        # Parse the KML file
        with open(kml_file, 'r', encoding='utf-8') as file:
            kml_content = file.read()
        
        # Parse the KML content with namespace handling
        kml_tree = ET.fromstring(kml_content)
        ns = {"kml": "http://www.opengis.net/kml/2.2"}  # Define the KML namespace
        gpx_tree = ET.Element("gpx", version="1.1", creator="KML to GPX Converter")

        # Handle <Point> elements (waypoints)
        placemarks_with_points = kml_tree.findall(".//kml:Placemark", ns)
        for placemark in placemarks_with_points:
            point = placemark.find("kml:Point", ns)
            coordinates = placemark.find("kml:Point/kml:coordinates", ns)
            if point is not None and coordinates is not None and coordinates.text:
                name = placemark.findtext("kml:name", default="", namespaces=ns)
                coord_text = coordinates.text.strip()
                lon, lat, *_ = coord_text.split(",")  # Extract longitude and latitude
                wpt = ET.SubElement(gpx_tree, "wpt", lat=lat, lon=lon)
                if name:
                    ET.SubElement(wpt, "name").text = name

        # Handle <LineString> elements (tracks)
        for placemark in kml_tree.findall(".//kml:Placemark", ns):
            line_string = placemark.find("kml:LineString", ns)
            coordinates = placemark.find("kml:LineString/kml:coordinates", ns)
            if line_string is not None and coordinates is not None and coordinates.text:
                name = placemark.findtext("kml:name", default="", namespaces=ns)
                coord_text = coordinates.text.strip()
                coord_list = coord_text.split()
                
                # Create a track in the GPX file
                trk = ET.SubElement(gpx_tree, "trk")
                if name:
                    ET.SubElement(trk, "name").text = name
                trkseg = ET.SubElement(trk, "trkseg")
                
                for coord in coord_list:
                    lon, lat, *_ = coord.split(",")
                    ET.SubElement(trkseg, "trkpt", lat=lat, lon=lon)
        
        # Write GPX to file
        ET.indent(gpx_tree, space="  ")
        with open(gpx_file, 'wb') as file:
            file.write(ET.tostring(gpx_tree, xml_declaration=True, encoding='UTF-8'))
        
        print(f"Conversion successful! GPX saved at: {gpx_file}")
    except Exception as e:
        print(f"Error during conversion: {e}")

def get_output_directory():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def main():
    # Hide the root tkinter window
    root = Tk()
    root.withdraw()

    # Open file dialog to select the .kml file
    kml_file = askopenfilename(
        title="Select a .kml file",
        filetypes=[("KML files", "*.kml")]
    )
    if not kml_file:
        print("No file selected. Exiting.")
        return

    # Get the directory of the script/executable
    script_dir = get_output_directory()

    # Generate the output .gpx file path
    base_name = os.path.splitext(os.path.basename(kml_file))[0]
    gpx_file = os.path.join(script_dir, f"{base_name} GPX.gpx")

    # Convert KML to GPX
    kml_to_gpx(kml_file, gpx_file)

if __name__ == "__main__":
    main()
