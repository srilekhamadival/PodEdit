"""
Minimal XML Test - Single Clip
If this imports successfully, we know the structure is correct
"""

def create_minimal_test_xml():
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xmeml>
<xmeml version="4">
  <sequence>
    <name>Test Sequence</name>
    <duration>900</duration>
    <rate>
      <timebase>30</timebase>
      <ntsc>FALSE</ntsc>
    </rate>
    <timecode>
      <rate>
        <timebase>30</timebase>
        <ntsc>FALSE</ntsc>
      </rate>
      <string>00:00:00:00</string>
      <frame>0</frame>
    </timecode>
    <media>
      <video>
        <format>
          <samplecharacteristics>
            <width>1920</width>
            <height>1080</height>
          </samplecharacteristics>
        </format>
        <track>
          <clipitem id="clip-1">
            <name>camera1_short.mp4</name>
            <duration>900</duration>
            <rate>
              <timebase>30</timebase>
              <ntsc>FALSE</ntsc>
            </rate>
            <start>0</start>
            <end>900</end>
            <in>0</in>
            <out>900</out>
          </clipitem>
        </track>
      </video>
    </media>
  </sequence>
</xmeml>"""
    
    with open("results/test_minimal.xml", "w", encoding="utf-8") as f:
        f.write(xml)
    
    print("✅ Minimal test XML created: results/test_minimal.xml")
    print("\nTry importing this first to test if Premiere accepts ANY XML from us.")

if __name__ == "__main__":
    create_minimal_test_xml()
