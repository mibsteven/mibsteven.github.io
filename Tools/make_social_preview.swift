import AppKit

let root = URL(fileURLWithPath: FileManager.default.currentDirectoryPath)
let outputURL = root.appendingPathComponent("assets/social-preview.png")
let size = CGSize(width: 1200, height: 630)
let image = NSImage(size: size)

func color(_ hex: UInt32, _ alpha: CGFloat = 1) -> NSColor {
    let r = CGFloat((hex >> 16) & 0xff) / 255
    let g = CGFloat((hex >> 8) & 0xff) / 255
    let b = CGFloat(hex & 0xff) / 255
    return NSColor(calibratedRed: r, green: g, blue: b, alpha: alpha)
}

func drawText(_ text: String, rect: CGRect, font: NSFont, color: NSColor, lineHeight: CGFloat? = nil) {
    let paragraph = NSMutableParagraphStyle()
    paragraph.lineBreakMode = .byWordWrapping
    if let lineHeight {
        paragraph.minimumLineHeight = lineHeight
        paragraph.maximumLineHeight = lineHeight
    }
    let attrs: [NSAttributedString.Key: Any] = [
        .font: font,
        .foregroundColor: color,
        .paragraphStyle: paragraph,
        .kern: 0
    ]
    NSString(string: text).draw(in: rect, withAttributes: attrs)
}

func drawRoundedImage(path: String, rect: CGRect, radius: CGFloat) {
    guard let icon = NSImage(contentsOf: root.appendingPathComponent(path)) else { return }
    NSGraphicsContext.saveGraphicsState()
    NSBezierPath(roundedRect: rect, xRadius: radius, yRadius: radius).addClip()
    icon.draw(in: rect, from: .zero, operation: .sourceOver, fraction: 1)
    NSGraphicsContext.restoreGraphicsState()
}

image.lockFocus()

let bounds = CGRect(origin: .zero, size: size)
let background = NSGradient(colors: [
    color(0xfbfaf8),
    color(0xf5f3ef),
    color(0xeee7dc)
])!
background.draw(in: NSBezierPath(rect: bounds), angle: -24)

color(0x161717, 0.045).setStroke()
for x in stride(from: 0, through: Int(size.width), by: 44) {
    NSBezierPath.strokeLine(from: CGPoint(x: x, y: 0), to: CGPoint(x: x, y: Int(size.height)))
}
for y in stride(from: 0, through: Int(size.height), by: 44) {
    NSBezierPath.strokeLine(from: CGPoint(x: 0, y: y), to: CGPoint(x: Int(size.width), y: y))
}

let card = CGRect(x: 70, y: 74, width: 1060, height: 482)
color(0xffffff, 0.82).setFill()
NSBezierPath(roundedRect: card, xRadius: 22, yRadius: 22).fill()
color(0x161717, 0.12).setStroke()
let border = NSBezierPath(roundedRect: card, xRadius: 22, yRadius: 22)
border.lineWidth = 1
border.stroke()

color(0xa8754e).setFill()
NSBezierPath(rect: CGRect(x: 122, y: 462, width: 52, height: 3)).fill()

drawText(
    "Apps by\nYu-Hsiang Chang",
    rect: CGRect(x: 122, y: 328, width: 600, height: 142),
    font: NSFont.systemFont(ofSize: 48, weight: .bold),
    color: color(0x161717),
    lineHeight: 55
)
drawText(
    "Thoughtful Apple apps for learning, creativity, and spatial experiences.",
    rect: CGRect(x: 124, y: 262, width: 620, height: 64),
    font: NSFont.systemFont(ofSize: 25, weight: .regular),
    color: color(0x45494d),
    lineHeight: 32
)
drawText(
    "為學習、創作與空間體驗打造的 Apple App",
    rect: CGRect(x: 124, y: 216, width: 620, height: 42),
    font: NSFont.systemFont(ofSize: 25, weight: .semibold),
    color: color(0x7b5135)
)

let pillLabels = ["Learning", "Creativity", "Personal Tools", "Spatial"]
var pillX: CGFloat = 124
for label in pillLabels {
    let width = CGFloat(label.count * 13 + 42)
    let rect = CGRect(x: pillX, y: 154, width: width, height: 42)
    color(0xf6f1e6, 0.92).setFill()
    NSBezierPath(roundedRect: rect, xRadius: 10, yRadius: 10).fill()
    color(0xa8754e, 0.22).setStroke()
    NSBezierPath(roundedRect: rect, xRadius: 10, yRadius: 10).stroke()
    drawText(label, rect: rect.insetBy(dx: 18, dy: 7), font: NSFont.systemFont(ofSize: 19, weight: .semibold), color: color(0x7b5135))
    pillX += width + 12
}

let iconPaths = [
    "assets/apps/zhuyin-story-icon.png",
    "assets/apps/objectifyar-icon.png",
    "assets/apps/english-saver-icon.png",
    "assets/apps/vectrafin-icon.png"
]
let iconRects = [
    CGRect(x: 788, y: 348, width: 132, height: 132),
    CGRect(x: 934, y: 348, width: 132, height: 132),
    CGRect(x: 788, y: 202, width: 132, height: 132),
    CGRect(x: 934, y: 202, width: 132, height: 132)
]

for (path, rect) in zip(iconPaths, iconRects) {
    color(0x161717, 0.14).setFill()
    NSBezierPath(roundedRect: rect.offsetBy(dx: 0, dy: -8), xRadius: 31, yRadius: 31).fill()
    drawRoundedImage(path: path, rect: rect, radius: 30)
}

drawText(
    "iPhone  iPad  Mac  Apple Vision Pro",
    rect: CGRect(x: 790, y: 112, width: 310, height: 28),
    font: NSFont.systemFont(ofSize: 19, weight: .medium),
    color: color(0x666b70)
)

image.unlockFocus()

guard
    let tiff = image.tiffRepresentation,
    let bitmap = NSBitmapImageRep(data: tiff),
    let data = bitmap.representation(using: .png, properties: [:])
else {
    fatalError("Could not render social preview image")
}

try data.write(to: outputURL)
print("Wrote \(outputURL.path)")
