const fs = require('fs-extra');
const path = require('path');

async function build() {
    console.log('🚀 Starting build process...');
    
    try {
        // Create dist directory
        const distDir = path.join(__dirname, 'dist');
        await fs.ensureDir(distDir);
        console.log('✅ Created dist directory');
        
        // Copy static assets
        const staticDir = path.join(__dirname, 'static');
        const distStaticDir = path.join(distDir, 'static');
        
        if (await fs.pathExists(staticDir)) {
            await fs.copy(staticDir, distStaticDir);
            console.log('✅ Copied static assets');
        }
        
        // Process HTML template
        const templatePath = path.join(__dirname, 'templates', 'index.html');
        const indexPath = path.join(distDir, 'index.html');
        
        if (await fs.pathExists(templatePath)) {
            let htmlContent = await fs.readFile(templatePath, 'utf8');
            
            // Replace Flask url_for template tags with static paths
            htmlContent = htmlContent.replace(
                /\{\{\s*url_for\('static',\s*filename='([^']+)'\)\s*\}\}/g,
                './static/$1'
            );
            
            // Add any additional processing here if needed
            
            await fs.writeFile(indexPath, htmlContent);
            console.log('✅ Processed index.html');
        }
        
        // Copy requirements.txt for Netlify Functions
        const requirementsPath = path.join(__dirname, 'requirements.txt');
        const distRequirementsPath = path.join(distDir, 'requirements.txt');
        
        if (await fs.pathExists(requirementsPath)) {
            await fs.copy(requirementsPath, distRequirementsPath);
            console.log('✅ Copied requirements.txt');
        }
        
        // Create _redirects file for SPA routing
        const redirectsContent = `
# API routes to Netlify Functions
/api/air-quality  /.netlify/functions/air-quality  200
/api/analyze  /.netlify/functions/analyze  200
/api/health-recommendations  /.netlify/functions/health-recommendations  200
/health  /.netlify/functions/health  200

# SPA fallback
/*  /index.html  200
        `.trim();
        
        await fs.writeFile(path.join(distDir, '_redirects'), redirectsContent);
        console.log('✅ Created _redirects file');
        
        console.log('🎉 Build completed successfully!');
        
    } catch (error) {
        console.error('❌ Build failed:', error);
        process.exit(1);
    }
}

build();