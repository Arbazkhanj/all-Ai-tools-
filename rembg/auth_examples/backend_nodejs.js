/**
 * Google One Tap Sign-In Backend - Node.js (Express)
 * ==================================================
 * 
 * This backend handles Google OAuth 2.0 authentication using ID tokens.
 * It verifies the token, extracts user info, and manages user sessions.
 * 
 * Installation:
 * npm install express cors jsonwebtoken google-auth-library bcryptjs
 */

const express = require('express');
const cors = require('cors');
const jwt = require('jsonwebtoken');
const { OAuth2Client } = require('google-auth-library');
require('dotenv').config();

// ============================================
// CONFIGURATION
// ============================================

const GOOGLE_CLIENT_ID = process.env.GOOGLE_CLIENT_ID || 'YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com';
const JWT_SECRET = process.env.JWT_SECRET || require('crypto').randomBytes(32).toString('hex');
const JWT_EXPIRATION = '24h';
const PORT = process.env.PORT || 8000;

// Initialize Google OAuth client
const googleClient = new OAuth2Client(GOOGLE_CLIENT_ID);

const app = express();

// Middleware
app.use(express.json());
app.use(cors({
    origin: ['http://localhost:7860', 'http://127.0.0.1:7860', 'https://yourdomain.com'],
    credentials: true
}));

// ============================================
// DATABASE (Use real database in production)
// ============================================

// In-memory database for demo - Replace with MongoDB/PostgreSQL
const usersDB = new Map();
const sessionsDB = new Map();

class User {
    constructor(googleId, email, name, picture = null) {
        this.id = require('crypto').randomBytes(16).toString('hex');
        this.googleId = googleId;
        this.email = email;
        this.name = name;
        this.picture = picture;
        this.createdAt = new Date();
        this.lastLogin = new Date();
        this.loginCount = 1;
    }
}

// ============================================
// JWT UTILITIES
// ============================================

function generateToken(user) {
    return jwt.sign(
        { 
            sub: user.id, 
            email: user.email, 
            name: user.name 
        },
        JWT_SECRET,
        { expiresIn: JWT_EXPIRATION }
    );
}

function verifyToken(token) {
    try {
        return jwt.verify(token, JWT_SECRET);
    } catch (error) {
        return null;
    }
}

// ============================================
// GOOGLE TOKEN VERIFICATION
// ============================================

async function verifyGoogleToken(idToken) {
    try {
        const ticket = await googleClient.verifyIdToken({
            idToken: idToken,
            audience: GOOGLE_CLIENT_ID,
        });

        const payload = ticket.getPayload();
        
        // Verify issuer
        if (!['accounts.google.com', 'https://accounts.google.com'].includes(payload.iss)) {
            throw new Error('Invalid issuer');
        }

        return payload;
    } catch (error) {
        console.error('Google token verification failed:', error);
        return null;
    }
}

// ============================================
// USER MANAGEMENT
// ============================================

function getOrCreateUser(googleUserInfo) {
    const googleId = googleUserInfo.sub;
    const email = googleUserInfo.email;
    const name = googleUserInfo.name || email.split('@')[0];
    const picture = googleUserInfo.picture;

    // Find existing user
    let existingUser = null;
    for (const user of usersDB.values()) {
        if (user.googleId === googleId) {
            existingUser = user;
            break;
        }
    }

    if (existingUser) {
        // Update login info
        existingUser.lastLogin = new Date();
        existingUser.loginCount += 1;
        if (picture) existingUser.picture = picture;
        console.log(`User logged in: ${email} (Login #${existingUser.loginCount})`);
        return existingUser;
    } else {
        // Create new user
        const newUser = new User(googleId, email, name, picture);
        usersDB.set(newUser.id, newUser);
        console.log(`New user created: ${email}`);
        return newUser;
    }
}

function getUserById(userId) {
    return usersDB.get(userId);
}

// ============================================
// AUTHENTICATION MIDDLEWARE
// ============================================

function authenticateToken(req, res, next) {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN

    if (!token) {
        return res.status(401).json({ error: 'Access token required' });
    }

    const payload = verifyToken(token);
    if (!payload) {
        return res.status(403).json({ error: 'Invalid or expired token' });
    }

    req.userId = payload.sub;
    req.userEmail = payload.email;
    next();
}

// ============================================
// API ROUTES
// ============================================

/**
 * POST /auth/google/token
 * Handle Google One Tap / Sign-In token
 */
app.post('/auth/google/token', async (req, res) => {
    try {
        const { credential, client_id } = req.body;

        if (!credential) {
            return res.status(400).json({
                success: false,
                message: 'Missing credential'
            });
        }

        // Step 1: Verify Google token
        const googleUserInfo = await verifyGoogleToken(credential);
        
        if (!googleUserInfo) {
            return res.status(401).json({
                success: false,
                message: 'Invalid Google token'
            });
        }

        // Step 2: Get or create user
        const user = getOrCreateUser(googleUserInfo);

        // Step 3: Generate JWT
        const accessToken = generateToken(user);

        // Step 4: Return response
        res.json({
            success: true,
            message: 'Authentication successful',
            token: accessToken,
            user: {
                id: user.id,
                email: user.email,
                name: user.name,
                picture: user.picture,
                createdAt: user.createdAt,
                isNew: user.loginCount === 1
            }
        });

    } catch (error) {
        console.error('Auth error:', error);
        res.status(500).json({
            success: false,
            message: 'Authentication failed'
        });
    }
});

/**
 * GET /auth/me
 * Get current logged-in user info
 */
app.get('/auth/me', authenticateToken, (req, res) => {
    const user = getUserById(req.userId);
    
    if (!user) {
        return res.status(404).json({ error: 'User not found' });
    }

    res.json({
        id: user.id,
        email: user.email,
        name: user.name,
        picture: user.picture,
        lastLogin: user.lastLogin
    });
});

/**
 * GET /auth/logout
 * Logout user
 */
app.get('/auth/logout', authenticateToken, (req, res) => {
    // In production, add token to blacklist
    res.json({ success: true, message: 'Logged out successfully' });
});

/**
 * GET /auth/users
 * Admin endpoint - list all users
 */
app.get('/auth/users', (req, res) => {
    const users = Array.from(usersDB.values()).map(u => ({
        id: u.id,
        email: u.email,
        name: u.name,
        loginCount: u.loginCount,
        lastLogin: u.lastLogin
    }));

    res.json({
        totalUsers: usersDB.size,
        users: users
    });
});

// ============================================
// PROTECTED ROUTES
// ============================================

/**
 * GET /api/protected
 * Example protected route
 */
app.get('/api/protected', authenticateToken, (req, res) => {
    res.json({
        message: 'This is a protected route',
        user: req.userEmail,
        timestamp: new Date().toISOString()
    });
});

/**
 * GET /api/user/history
 * Get user's processing history (example)
 */
app.get('/api/user/history', authenticateToken, (req, res) => {
    // In production, fetch from database
    res.json({
        userId: req.userId,
        history: [
            { id: 1, filename: 'image1.png', date: new Date().toISOString() },
            { id: 2, filename: 'image2.jpg', date: new Date().toISOString() }
        ]
    });
});

// ============================================
// HEALTH CHECK
// ============================================

app.get('/health', (req, res) => {
    res.json({
        status: 'healthy',
        googleClientId: GOOGLE_CLIENT_ID !== 'YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com',
        timestamp: new Date().toISOString()
    });
});

// ============================================
// ERROR HANDLING
// ============================================

app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({ error: 'Something went wrong!' });
});

// ============================================
// START SERVER
// ============================================

app.listen(PORT, () => {
    console.log('='.repeat(50));
    console.log('Google One Tap Auth API Server (Node.js)');
    console.log('='.repeat(50));
    console.log(`Server running on http://localhost:${PORT}`);
    console.log(`JWT Secret: ${JWT_SECRET.substring(0, 10)}...`);
    
    if (GOOGLE_CLIENT_ID === 'YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com') {
        console.log('⚠️  WARNING: Google Client ID not configured!');
        console.log('   Set GOOGLE_CLIENT_ID in environment variables.');
    } else {
        console.log(`Google Client ID: ${GOOGLE_CLIENT_ID.substring(0, 20)}...`);
    }
    console.log('='.repeat(50));
});

module.exports = app;
