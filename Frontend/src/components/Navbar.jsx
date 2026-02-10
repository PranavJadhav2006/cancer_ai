import React, { useState, useEffect } from 'react';
import { 
  AppBar, 
  Toolbar, 
  Typography, 
  Button, 
  Box, 
  Container, 
  IconButton, 
  Drawer, 
  List, 
  ListItem, 
  ListItemText,
  ListItemButton
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline';
import { motion } from 'framer-motion';
import { Link, useLocation } from 'react-router-dom';
import { HashLink } from 'react-router-hash-link';
import Logo from './Logo';
import './Navbar.css';

const navLinks = [
  { title: 'Home', path: '/' },
  { title: 'Dashboard', path: '/dashboard' },
  { title: 'About', path: '/about' },
];

const Navbar = () => {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const location = useLocation();

  // Handle Scroll Effect
  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const isCurrentPath = (path) => {
    if (path === '/' && location.pathname !== '/') return false;
    return location.pathname.startsWith(path);
  };

  return (
    <>
      <AppBar 
        position="fixed" 
        elevation={0}
        className={`app-bar-root ${scrolled ? 'app-bar-scrolled' : ''}`}
      >
        <Container maxWidth="xl">
          <Toolbar disableGutters sx={{ justifyContent: 'space-between' }}>
            
            {/* --- LOGO SECTION --- */}
            <Link to="/" style={{ textDecoration: 'none' }}>
              <Logo size={45} />
            </Link>

            {/* --- DESKTOP MENU --- */}
            <Box sx={{ display: { xs: 'none', md: 'flex' }, gap: 4, alignItems: 'center' }}>
              {navLinks.map((link) => {
                const isHash = link.path.includes('#');
                return (
                  <Button
                    key={link.title}
                    component={isHash ? HashLink : Link}
                    to={link.path}
                    {...(isHash ? { smooth: true } : {})}
                    className={`nav-link-btn ${isCurrentPath(link.path) ? 'active' : ''}`}
                  >
                    {link.title}
                  </Button>
                );
              })}
            </Box>

            {/* --- ACTION BUTTONS --- */}
            <Box sx={{ display: { xs: 'none', md: 'flex' }, gap: 2 }}>
              <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                <Button 
                  component={Link}
                  to="/login"
                  variant="text" 
                  className="nav-secondary-btn"
                >
                  Login
                </Button>
              </motion.div>
              <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                <Button 
                  component={Link}
                  to="/patients"
                  variant="outlined" 
                  startIcon={<AddCircleOutlineIcon />}
                  className="nav-action-btn"
                >
                  Initialize Case
                </Button>
              </motion.div>
            </Box>

            {/* --- MOBILE BURGER MENU --- */}
            <IconButton
              color="inherit"
              aria-label="open drawer"
              edge="start"
              onClick={handleDrawerToggle}
              sx={{ display: { md: 'none' }, color: '#059789' }}
            >
              <MenuIcon />
            </IconButton>
          </Toolbar>
        </Container>
      </AppBar>

      {/* --- MOBILE DRAWER (Slide in from right) --- */}
      <Drawer
        anchor="right"
        open={mobileOpen}
        onClose={handleDrawerToggle}
        classes={{ paper: 'mobile-drawer-paper' }}
      >
        <List sx={{ mt: 5 }}>
          {navLinks.map((link) => {
            const isHash = link.path.includes('#');
            return (
              <ListItem key={link.title} disablePadding>
                <ListItemButton 
                  component={isHash ? HashLink : Link}
                  to={link.path}
                  {...(isHash ? { smooth: true } : {})}
                  onClick={handleDrawerToggle}
                  className="mobile-nav-item-btn"
                >
                  <ListItemText 
                    primary={link.title} 
                    primaryTypographyProps={{ 
                      style: { color: isCurrentPath(link.path) ? '#00F0FF' : '#F8FAFC' } 
                    }} 
                  />
                </ListItemButton>
              </ListItem>
            );
          })}
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
            <Button 
              component={Link}
              to="/patients"
              onClick={handleDrawerToggle}
              variant="contained" 
              className="mobile-action-btn"
            >
              Initialize New Case
            </Button>
          </Box>
        </List>
      </Drawer>
    </>
  );
};

export default Navbar;
