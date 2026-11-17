"""Render video.html frame-by-frame via headless Chrome. Usage: capture.py all | capture.py t1 t2 ..."""
import base64, sys, pathlib
from selenium import webdriver

W, H, FPS, DUR = 1920, 1080, 30, 20
here = pathlib.Path(__file__).parent
o = webdriver.ChromeOptions()
o.add_argument("--headless=new"); o.add_argument("--hide-scrollbars"); o.add_argument("--force-device-scale-factor=1")
d = webdriver.Chrome(options=o)
d.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", {"width": W, "height": H, "deviceScaleFactor": 1, "mobile": False})
d.get((here / "video.html").as_uri())
d.execute_async_script("const cb=arguments[0];document.fonts.ready.then(()=>cb(document.fonts.check('40px \"JetBrains Mono\"')))")
print("fonts ok:", d.execute_script("return document.fonts.check('40px \"JetBrains Mono\"') && document.fonts.check('700 40px \"Space Grotesk\"')"))

def shot(t, path):
    d.execute_script(f"render({t})")
    png = d.execute_cdp_cmd("Page.captureScreenshot", {"format": "png", "clip": {"x": 0, "y": 0, "width": W, "height": H, "scale": 1}})
    path.write_bytes(base64.b64decode(png["data"]))

if sys.argv[1] == "all":
    out = here / "frames"; out.mkdir(exist_ok=True)
    for i in range(FPS * DUR):
        shot(i / FPS, out / f"f{i:04d}.png")
else:
    for t in sys.argv[1:]:
        shot(float(t), here / f"still_{t}.png")
d.quit()
