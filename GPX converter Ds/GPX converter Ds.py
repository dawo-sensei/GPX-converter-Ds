import os
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from lxml import etree

def kml_to_gpx(kml_file, gpx_file):
    """
    Converts a .kml file to a .gpx file.
    """
    try:
        # Parse the KML file
        with open(kml_file, 'r', encoding='utf-8') as file:
            kml_content = file.read()
        
        # Parse the KML content with namespace handling
        kml_tree = etree.fromstring(kml_content.encode('utf-8'))
        ns = {"kml": "http://www.opengis.net/kml/2.2"}  # Define the KML namespace
        gpx_tree = etree.Element("gpx", version="1.1", creator="KML to GPX Converter")
        
        # Handle <Point> elements (waypoints)
        placemarks_with_points = kml_tree.xpath(".//kml:Placemark[kml:Point]", namespaces=ns)
        for placemark in placemarks_with_points:
            name = placemark.findtext("kml:name", namespaces=ns)
            coordinates = placemark.xpath("kml:Point/kml:coordinates", namespaces=ns)
            if coordinates:
                coord_text = coordinates[0].text.strip()
                lon, lat, *_ = coord_text.split(",")  # Extract longitude and latitude
                wpt = etree.SubElement(gpx_tree, "wpt", lat=lat, lon=lon)
                if name:
                    etree.SubElement(wpt, "name").text = name
        
        # Handle <LineString> elements (tracks)
        placemarks_with_lines = kml_tree.xpath(".//kml:Placemark[kml:LineString]", namespaces=ns)
        for placemark in placemarks_with_lines:
            name = placemark.findtext("kml:name", namespaces=ns)
            coordinates = placemark.xpath("kml:LineString/kml:coordinates", namespaces=ns)
            if coordinates:
                coord_text = coordinates[0].text.strip()
                coord_list = coord_text.split()
                
                # Create a track in the GPX file
                trk = etree.SubElement(gpx_tree, "trk")
                if name:
                    etree.SubElement(trk, "name").text = name
                trkseg = etree.SubElement(trk, "trkseg")
                
                for coord in coord_list:
                    lon, lat, *_ = coord.split(",")
                    etree.SubElement(trkseg, "trkpt", lat=lat, lon=lon)
        
        # Write GPX to file
        with open(gpx_file, 'wb') as file:
            file.write(etree.tostring(gpx_tree, pretty_print=True, xml_declaration=True, encoding='UTF-8'))
        
        print(f"Conversion successful! GPX saved at: {gpx_file}")
    except Exception as e:
        print(f"Error during conversion: {e}")

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
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Generate the output .gpx file path
    base_name = os.path.splitext(os.path.basename(kml_file))[0]
    gpx_file = os.path.join(script_dir, f"{base_name} GPX.gpx")

    # Convert KML to GPX
    kml_to_gpx(kml_file, gpx_file)

if __name__ == "__main__":
    main()