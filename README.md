# smin987 Homebrew Tap

Official Homebrew Tap for [Image Optimizer](https://github.com/smin987/ImageOptimizer).

## Installation

\\ash
brew tap smin987/tap
brew install --cask image-optimizer
\EOF
git add .
git commit -m 'feat: Add image-optimizer cask'
gh repo create homebrew-tap --public --description 'Official Homebrew Tap for Image Optimizer' --source=. --remote=origin --push
rm -rf 
