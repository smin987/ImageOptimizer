cask "image-optimizer" do
  version "1.0.4"
  sha256 :no_check

  url "https://github.com/smin987/ImageOptimizer/releases/download/v#{version}/ImageOptimizer-macos.dmg"
  name "Image Optimizer"
  desc "All-in-one cross-platform image and animated GIF optimizer for web and desktop"
  homepage "https://github.com/smin987/ImageOptimizer"
  license :freeware

  livecheck do
    url :url
    strategy :github_latest
  end

  auto_updates true
  depends_on macos: ">= :catalina"

  app "ImageOptimizer.app"
  binary "#{appdir}/ImageOptimizer.app/Contents/MacOS/ImageOptimizer", target: "image-optimizer"
  binary "#{appdir}/ImageOptimizer.app/Contents/MacOS/ImageOptimizer", target: "iopt"

  zap trash: [
    "~/Library/Application Support/ImageOptimizer",
    "~/Library/Saved Application State/mycompany.imageoptimizer.app.v1.savedState",
  ]
end
