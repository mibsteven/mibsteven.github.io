import AppKit

let root = URL(fileURLWithPath: FileManager.default.currentDirectoryPath)
let outputURL = root.appendingPathComponent("assets/facebook-cover.png")
let size = CGSize(width: 1640, height: 624)
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
NSGradient(colors: [
    color(0xfbfaf8),
    color(0xf4efe6),
    color(0xe9edf0)
])!.draw(in: NSBezierPath(rect: bounds), angle: -18)

color(0x161717, 0.04).setStroke()
for x in stride(from: 0, through: Int(size.width), by: 44) {
    NSBezierPath.strokeLine(from: CGPoint(x: x, y: 0), to: CGPoint(x: x, y: Int(size.height)))
}
for y in stride(from: 0, through: Int(size.height), by: 44) {
    NSBezierPath.strokeLine(from: CGPoint(x: 0, y: y), to: CGPoint(x: Int(size.width), y: y))
}

let card = CGRect(x: 92, y: 74, width: 1456, height: 476)
color(0xffffff, 0.78).setFill()
NSBezierPath(roundedRect: card, xRadius: 26, yRadius: 26).fill()
color(0x161717, 0.12).setStroke()
let cardBorder = NSBezierPath(roundedRect: card, xRadius: 26, yRadius: 26)
cardBorder.lineWidth = 1
cardBorder.stroke()

color(0xa8754e).setFill()
NSBezierPath(rect: CGRect(x: 160, y: 438, width: 56, height: 4)).fill()

drawText(
    "Apps by\nYu-Hsiang Chang",
    rect: CGRect(x: 160, y: 286, width: 680, height: 148),
    font: NSFont.systemFont(ofSize: 48, weight: .bold),
    color: color(0x161717),
    lineHeight: 56
)
drawText(
    "Thoughtful Apple apps for learning, creativity, and spatial experiences.",
    rect: CGRect(x: 162, y: 224, width: 710, height: 58),
    font: NSFont.systemFont(ofSize: 24, weight: .regular),
    color: color(0x45494d),
    lineHeight: 31
)
drawText(
    "為學習、創作與空間體驗打造的 Apple App",
    rect: CGRect(x: 162, y: 184, width: 720, height: 34),
    font: NSFont.systemFont(ofSize: 24, weight: .semibold),
    color: color(0x7b5135)
)

let labels = ["Learning", "Creativity", "Personal Tools", "Spatial"]
var x: CGFloat = 162
for label in labels {
    let width = CGFloat(label.count * 13 + 48)
    let rect = CGRect(x: x, y: 128, width: width, height: 42)
    color(0xf8f2e9, 0.9).setFill()
    NSBezierPath(roundedRect: rect, xRadius: 10, yRadius: 10).fill()
    color(0xa8754e, 0.22).setStroke()
    NSBezierPath(roundedRect: rect, xRadius: 10, yRadius: 10).stroke()
    drawText(label, rect: rect.insetBy(dx: 18, dy: 8), font: NSFont.systemFont(ofSize: 20, weight: .semibold), color: color(0x7b5135))
    x += width + 14
}

let iconPaths = [
    "assets/apps/zhuyin-story-icon.png",
    "assets/apps/objectifyar-icon.png",
    "assets/apps/english-saver-icon.png",
    "assets/apps/vectrafin-icon.png"
]
let iconSize: CGFloat = 126
let startX: CGFloat = 1038
let startY: CGFloat = 312
let gap: CGFloat = 22
let iconRects = [
    CGRect(x: startX, y: startY, width: iconSize, height: iconSize),
    CGRect(x: startX + iconSize + gap, y: startY, width: iconSize, height: iconSize),
    CGRect(x: startX, y: startY - iconSize - gap, width: iconSize, height: iconSize),
    CGRect(x: startX + iconSize + gap, y: startY - iconSize - gap, width: iconSize, height: iconSize)
]

for (path, rect) in zip(iconPaths, iconRects) {
    color(0x161717, 0.16).setFill()
    NSBezierPath(roundedRect: rect.offsetBy(dx: 0, dy: -9), xRadius: 29, yRadius: 29).fill()
    drawRoundedImage(path: path, rect: rect, radius: 28)
}

drawText(
    "iPhone  iPad  Mac  Apple Vision Pro",
    rect: CGRect(x: 1004, y: 118, width: 360, height: 28),
    font: NSFont.systemFont(ofSize: 20, weight: .medium),
    color: color(0x666b70)
)

image.unlockFocus()

guard
    let tiff = image.tiffRepresentation,
    let bitmap = NSBitmapImageRep(data: tiff),
    let data = bitmap.representation(using: .png, properties: [:])
else {
    fatalError("Could not render Facebook cover")
}

try data.write(to: outputURL)
print("Wrote \(outputURL.path)")
