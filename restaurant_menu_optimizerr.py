#!/usr/bin/env python3
"""
Restaurant Menu Optimizer - Single File Flask Application
Complete menu analysis and optimization tool for restaurants
Run with: python restaurant_menu_optimizer.py
"""

from flask import Flask, render_template_string, request, jsonify
import json
import random
import time
from datetime import datetime, timedelta
import webbrowser
from threading import Timer
import math

app = Flask(__name__)

# HTML Template (embedded)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Restaurant Menu Optimizer</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #ff6b6b 0%, #feca57 100%); min-height: 100vh; color: #333; }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        .header { background: rgba(255, 255, 255, 0.95); border-radius: 15px; padding: 30px; text-align: center; margin-bottom: 30px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1); backdrop-filter: blur(10px); }
        .header h1 { color: #d63031; font-size: 2.5rem; margin-bottom: 10px; }
        .header p { color: #666; font-size: 1.2rem; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: rgba(255, 255, 255, 0.95); border-radius: 15px; padding: 25px; display: flex; align-items: center; cursor: pointer; transition: transform 0.3s ease, box-shadow 0.3s ease; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1); }
        .stat-card:hover { transform: translateY(-5px); box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15); }
        .stat-icon { background: #ff6b6b; color: white; width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; margin-right: 20px; }
        .stat-content h3 { font-size: 2rem; color: #d63031; margin-bottom: 5px; }
        .stat-content p { color: #666; font-size: 1rem; }
        .main-content { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-bottom: 30px; }
        .section { background: rgba(255, 255, 255, 0.95); border-radius: 15px; padding: 30px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1); }
        .section h2 { color: #d63031; margin-bottom: 25px; font-size: 1.8rem; }
        .form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .form-group { display: flex; flex-direction: column; }
        .form-group label { color: #555; margin-bottom: 8px; font-weight: 600; }
        .form-group input, .form-group select, .form-group textarea { padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 1rem; transition: border-color 0.3s ease; }
        .form-group input:focus, .form-group select:focus, .form-group textarea:focus { outline: none; border-color: #ff6b6b; }
        .form-group textarea { min-height: 100px; resize: vertical; }
        .btn { background: linear-gradient(135deg, #ff6b6b, #ee5a52); color: white; border: none; padding: 15px 30px; font-size: 1.1rem; border-radius: 10px; cursor: pointer; transition: transform 0.3s ease; width: 100%; margin-bottom: 15px; }
        .btn:hover { transform: translateY(-2px); }
        .btn-secondary { background: linear-gradient(135deg, #74b9ff, #0984e3); }
        .menu-item { background: #f8f9fa; border-radius: 10px; padding: 20px; margin-bottom: 15px; border-left: 4px solid #ff6b6b; }
        .menu-item h4 { color: #d63031; margin-bottom: 10px; font-size: 1.2rem; }
        .menu-item-details { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; font-size: 0.9rem; color: #666; }
        .recommendation { background: #e8f5e8; border-left: 4px solid #00b894; padding: 20px; margin-bottom: 15px; border-radius: 0 10px 10px 0; }
        .recommendation.warning { background: #fff3cd; border-left-color: #ffc107; }
        .recommendation.danger { background: #f8d7da; border-left-color: #dc3545; }
        .recommendation h3 { margin-bottom: 10px; }
        .recommendation p { line-height: 1.6; }
        .charts-section { background: rgba(255, 255, 255, 0.95); border-radius: 15px; padding: 30px; margin-bottom: 30px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1); }
        .chart-container { height: 350px; background: #f8f9fa; border-radius: 10px; padding: 20px; margin-bottom: 20px; }
        .loading-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.8); display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 1000; color: white; }
        .spinner { width: 50px; height: 50px; border: 5px solid #333; border-top: 5px solid #ff6b6b; border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 20px; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .no-data { text-align: center; color: #999; font-style: italic; padding: 40px; }
        @media (max-width: 768px) { .main-content { grid-template-columns: 1fr; } .form-grid { grid-template-columns: 1fr; } .stats-grid { grid-template-columns: repeat(2, 1fr); } .header h1 { font-size: 2rem; } .container { padding: 15px; } }
        @media (max-width: 480px) { .stats-grid { grid-template-columns: 1fr; } }
        .profit-badge { background: #00b894; color: white; padding: 4px 8px; border-radius: 12px; font-size: 0.8rem; font-weight: bold; }
        .loss-badge { background: #e17055; color: white; padding: 4px 8px; border-radius: 12px; font-size: 0.8rem; font-weight: bold; }
        .neutral-badge { background: #74b9ff; color: white; padding: 4px 8px; border-radius: 12px; font-size: 0.8rem; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1><i class="fas fa-utensils"></i> Restaurant Menu Optimizer</h1>
            <p>AI-Powered Menu Analysis & Profit Optimization</p>
        </header>

        <section class="stats-section">
            <div class="stats-grid">
                <div class="stat-card" onclick="showStatInfo('revenue')">
                    <div class="stat-icon"><i class="fas fa-dollar-sign"></i></div>
                    <div class="stat-content">
                        <h3 id="total-revenue">$0</h3>
                        <p>Monthly Revenue</p>
                    </div>
                </div>
                <div class="stat-card" onclick="showStatInfo('items')">
                    <div class="stat-icon"><i class="fas fa-list"></i></div>
                    <div class="stat-content">
                        <h3 id="menu-items">0</h3>
                        <p>Menu Items</p>
                    </div>
                </div>
                <div class="stat-card" onclick="showStatInfo('margin')">
                    <div class="stat-icon"><i class="fas fa-chart-line"></i></div>
                    <div class="stat-content">
                        <h3 id="avg-margin">0%</h3>
                        <p>Avg Profit Margin</p>
                    </div>
                </div>
                <div class="stat-card" onclick="showStatInfo('bestseller')">
                    <div class="stat-icon"><i class="fas fa-star"></i></div>
                    <div class="stat-content">
                        <h3 id="bestseller">-</h3>
                        <p>Top Seller</p>
                    </div>
                </div>
            </div>
        </section>

        <div class="main-content">
            <section class="section">
                <h2><i class="fas fa-plus"></i> Add Menu Item</h2>
                <form id="menu-form">
                    <div class="form-grid">
                        <div class="form-group">
                            <label for="item-name">Item Name</label>
                            <input type="text" id="item-name" placeholder="e.g., Grilled Salmon" required>
                        </div>
                        <div class="form-group">
                            <label for="category">Category</label>
                            <select id="category" required>
                                <option value="">Select category</option>
                                <option value="Appetizers">Appetizers</option>
                                <option value="Main Courses">Main Courses</option>
                                <option value="Desserts">Desserts</option>
                                <option value="Beverages">Beverages</option>
                                <option value="Salads">Salads</option>
                                <option value="Soups">Soups</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="selling-price">Selling Price ($)</label>
                            <input type="number" id="selling-price" step="0.01" min="0" placeholder="24.99" required>
                        </div>
                        <div class="form-group">
                            <label for="food-cost">Food Cost ($)</label>
                            <input type="number" id="food-cost" step="0.01" min="0" placeholder="8.50" required>
                        </div>
                        <div class="form-group">
                            <label for="prep-time">Prep Time (minutes)</label>
                            <input type="number" id="prep-time" min="0" placeholder="15" required>
                        </div>
                        <div class="form-group">
                            <label for="monthly-sales">Monthly Sales (units)</label>
                            <input type="number" id="monthly-sales" min="0" placeholder="120" required>
                        </div>
                    </div>
                    <div class="form-group">
                        <label for="ingredients">Ingredients (one per line)</label>
                        <textarea id="ingredients" placeholder="Salmon fillet&#10;Lemon&#10;Herbs&#10;Olive oil"></textarea>
                    </div>
                    <button type="submit" class="btn">
                        <i class="fas fa-plus"></i> Add Item to Menu
                    </button>
                </form>
            </section>

            <section class="section">
                <h2><i class="fas fa-chart-bar"></i> Quick Analysis</h2>
                <button onclick="generateReport()" class="btn">
                    <i class="fas fa-chart-line"></i> Generate Profit Analysis
                </button>
                <button onclick="optimizePricing()" class="btn btn-secondary">
                    <i class="fas fa-dollar-sign"></i> Optimize Pricing
                </button>
                <button onclick="identifyTrends()" class="btn">
                    <i class="fas fa-trending-up"></i> Identify Trends
                </button>
                <button onclick="costAnalysis()" class="btn btn-secondary">
                    <i class="fas fa-calculator"></i> Cost Analysis
                </button>
            </section>
        </div>

        <section class="section" id="menu-display">
            <h2><i class="fas fa-list"></i> Current Menu</h2>
            <div id="menu-items-container">
                <p class="no-data">No menu items added yet. Add your first item above!</p>
            </div>
        </section>

        <section class="section" id="recommendations-section" style="display: none;">
            <h2><i class="fas fa-lightbulb"></i> Optimization Recommendations</h2>
            <div id="recommendations-container"></div>
        </section>

        <section class="charts-section" id="charts-section" style="display: none;">
            <h2><i class="fas fa-chart-pie"></i> Performance Analytics</h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px;">
                <div class="chart-container">
                    <h3 style="text-align: center; margin-bottom: 15px; color: #d63031;">Profit by Category</h3>
                    <canvas id="profitChart"></canvas>
                </div>
                <div class="chart-container">
                    <h3 style="text-align: center; margin-bottom: 15px; color: #d63031;">Sales Volume Trends</h3>
                    <canvas id="salesChart"></canvas>
                </div>
                <div class="chart-container">
                    <h3 style="text-align: center; margin-bottom: 15px; color: #d63031;">Profit Margin Distribution</h3>
                    <canvas id="marginChart"></canvas>
                </div>
                <div class="chart-container">
                    <h3 style="text-align: center; margin-bottom: 15px; color: #d63031;">Cost vs Price Analysis</h3>
                    <canvas id="costChart"></canvas>
                </div>
            </div>
        </section>
    </div>

    <div id="loading-overlay" class="loading-overlay" style="display: none;">
        <div class="spinner"></div>
        <p>Analyzing menu data...</p>
    </div>

    <script>
        let menuItems = [];
        let currentAnalysis = null;

        document.addEventListener('DOMContentLoaded', function() {
            setupFormSubmission();
            updateDisplay();
        });

        function setupFormSubmission() {
            const form = document.getElementById('menu-form');
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                addMenuItem();
            });
        }

        function addMenuItem() {
            const formData = {
                name: document.getElementById('item-name').value,
                category: document.getElementById('category').value,
                sellingPrice: parseFloat(document.getElementById('selling-price').value),
                foodCost: parseFloat(document.getElementById('food-cost').value),
                prepTime: parseInt(document.getElementById('prep-time').value),
                monthlySales: parseInt(document.getElementById('monthly-sales').value),
                ingredients: document.getElementById('ingredients').value.split('\\n').filter(i => i.trim())
            };

            document.getElementById('loading-overlay').style.display = 'flex';

            fetch('/api/menu-item', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(result => {
                document.getElementById('loading-overlay').style.display = 'none';
                if (result.success) {
                    menuItems = result.menuItems;
                    updateDisplay();
                    document.getElementById('menu-form').reset();
                    showNotification('Menu item added successfully!', 'success');
                } else {
                    showNotification('Error: ' + result.error, 'error');
                }
            })
            .catch(error => {
                document.getElementById('loading-overlay').style.display = 'none';
                showNotification('Failed to add menu item. Please try again.', 'error');
            });
        }

        function updateDisplay() {
            updateStats();
            displayMenuItems();
        }

        function updateStats() {
            if (menuItems.length === 0) {
                document.getElementById('total-revenue').textContent = '$0';
                document.getElementById('menu-items').textContent = '0';
                document.getElementById('avg-margin').textContent = '0%';
                document.getElementById('bestseller').textContent = '-';
                return;
            }

            const totalRevenue = menuItems.reduce((sum, item) => sum + (item.sellingPrice * item.monthlySales), 0);
            const avgMargin = menuItems.reduce((sum, item) => {
                const margin = ((item.sellingPrice - item.foodCost) / item.sellingPrice) * 100;
                return sum + margin;
            }, 0) / menuItems.length;
            
            const bestseller = menuItems.reduce((max, item) => 
                item.monthlySales > max.monthlySales ? item : max, menuItems[0]);

            document.getElementById('total-revenue').textContent = '$' + totalRevenue.toLocaleString();
            document.getElementById('menu-items').textContent = menuItems.length;
            document.getElementById('avg-margin').textContent = Math.round(avgMargin) + '%';
            document.getElementById('bestseller').textContent = bestseller.name;
        }

        function displayMenuItems() {
            const container = document.getElementById('menu-items-container');
            
            if (menuItems.length === 0) {
                container.innerHTML = '<p class="no-data">No menu items added yet. Add your first item above!</p>';
                return;
            }

            container.innerHTML = menuItems.map(item => {
                const profit = item.sellingPrice - item.foodCost;
                const margin = ((profit / item.sellingPrice) * 100).toFixed(1);
                const monthlyProfit = profit * item.monthlySales;
                
                let badgeClass = 'neutral-badge';
                let badgeText = 'Normal';
                if (margin > 70) { badgeClass = 'profit-badge'; badgeText = 'High Margin'; }
                else if (margin < 30) { badgeClass = 'loss-badge'; badgeText = 'Low Margin'; }
                
                return `
                    <div class="menu-item">
                        <h4>${item.name} <span class="${badgeClass}">${badgeText}</span></h4>
                        <div class="menu-item-details">
                            <div><strong>Category:</strong> ${item.category}</div>
                            <div><strong>Price:</strong> $${item.sellingPrice.toFixed(2)}</div>
                            <div><strong>Food Cost:</strong> $${item.foodCost.toFixed(2)}</div>
                            <div><strong>Profit:</strong> $${profit.toFixed(2)} (${margin}%)</div>
                            <div><strong>Monthly Sales:</strong> ${item.monthlySales} units</div>
                            <div><strong>Monthly Profit:</strong> $${monthlyProfit.toFixed(2)}</div>
                            <div><strong>Prep Time:</strong> ${item.prepTime} min</div>
                        </div>
                    </div>
                `;
            }).join('');
        }

        function generateReport() {
            if (menuItems.length === 0) {
                showNotification('Add menu items first to generate a report.', 'warning');
                return;
            }

            document.getElementById('loading-overlay').style.display = 'flex';

            fetch('/api/analysis/profit')
            .then(response => response.json())
            .then(result => {
                document.getElementById('loading-overlay').style.display = 'none';
                displayRecommendations(result.recommendations);
                showChartsSection();
                showNotification('Profit analysis completed!', 'success');
            })
            .catch(error => {
                document.getElementById('loading-overlay').style.display = 'none';
                showNotification('Analysis failed. Please try again.', 'error');
            });
        }

        function optimizePricing() {
            if (menuItems.length === 0) {
                showNotification('Add menu items first to optimize pricing.', 'warning');
                return;
            }

            document.getElementById('loading-overlay').style.display = 'flex';

            fetch('/api/analysis/pricing')
            .then(response => response.json())
            .then(result => {
                document.getElementById('loading-overlay').style.display = 'none';
                displayRecommendations(result.recommendations);
                showNotification('Pricing optimization completed!', 'success');
            })
            .catch(error => {
                document.getElementById('loading-overlay').style.display = 'none';
                showNotification('Pricing optimization failed. Please try again.', 'error');
            });
        }

        function identifyTrends() {
            if (menuItems.length === 0) {
                showNotification('Add menu items first to identify trends.', 'warning');
                return;
            }

            document.getElementById('loading-overlay').style.display = 'flex';

            fetch('/api/analysis/trends')
            .then(response => response.json())
            .then(result => {
                document.getElementById('loading-overlay').style.display = 'none';
                displayRecommendations(result.recommendations);
                showNotification('Trend analysis completed!', 'success');
            })
            .catch(error => {
                document.getElementById('loading-overlay').style.display = 'none';
                showNotification('Trend analysis failed. Please try again.', 'error');
            });
        }

        function costAnalysis() {
            if (menuItems.length === 0) {
                showNotification('Add menu items first for cost analysis.', 'warning');
                return;
            }

            document.getElementById('loading-overlay').style.display = 'flex';

            fetch('/api/analysis/costs')
            .then(response => response.json())
            .then(result => {
                document.getElementById('loading-overlay').style.display = 'none';
                displayRecommendations(result.recommendations);
                showNotification('Cost analysis completed!', 'success');
            })
            .catch(error => {
                document.getElementById('loading-overlay').style.display = 'none';
                showNotification('Cost analysis failed. Please try again.', 'error');
            });
        }

        function displayRecommendations(recommendations) {
            const container = document.getElementById('recommendations-container');
            const section = document.getElementById('recommendations-section');
            
            container.innerHTML = recommendations.map(rec => `
                <div class="recommendation ${rec.type || ''}">
                    <h3>${rec.title}</h3>
                    <p>${rec.description}</p>
                </div>
            `).join('');
            
            section.style.display = 'block';
            section.scrollIntoView({ behavior: 'smooth' });
        }

        function showChartsSection() {
            document.getElementById('charts-section').style.display = 'block';
            generateCharts();
        }

        function generateCharts() {
            if (menuItems.length === 0) return;

            // Destroy existing charts
            Chart.helpers.each(Chart.instances, function(instance) {
                instance.destroy();
            });

            generateProfitChart();
            generateSalesChart();
            generateMarginChart();
            generateCostChart();
        }

        function generateProfitChart() {
            const ctx = document.getElementById('profitChart').getContext('2d');
            
            // Group by category
            const categoryData = {};
            menuItems.forEach(item => {
                if (!categoryData[item.category]) {
                    categoryData[item.category] = 0;
                }
                categoryData[item.category] += item.monthlyProfit;
            });

            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: Object.keys(categoryData),
                    datasets: [{
                        data: Object.values(categoryData),
                        backgroundColor: [
                            '#ff6b6b', '#74b9ff', '#00b894', '#feca57', 
                            '#e17055', '#a29bfe', '#fd79a8', '#fdcb6e'
                        ],
                        borderWidth: 2,
                        borderColor: '#fff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 20,
                                usePointStyle: true
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return context.label + ': $' + context.parsed.toLocaleString();
                                }
                            }
                        }
                    }
                }
            });
        }

        function generateSalesChart() {
            const ctx = document.getElementById('salesChart').getContext('2d');
            
            // Sort items by sales volume
            const sortedItems = [...menuItems].sort((a, b) => b.monthlySales - a.monthlySales);
            const topItems = sortedItems.slice(0, 8); // Show top 8 items

            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: topItems.map(item => item.name.length > 15 ? item.name.substring(0, 15) + '...' : item.name),
                    datasets: [{
                        label: 'Monthly Sales (Units)',
                        data: topItems.map(item => item.monthlySales),
                        backgroundColor: '#74b9ff',
                        borderColor: '#0984e3',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return 'Sales: ' + context.parsed.y + ' units';
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return value + ' units';
                                }
                            }
                        },
                        x: {
                            ticks: {
                                maxRotation: 45
                            }
                        }
                    }
                }
            });
        }

        function generateMarginChart() {
            const ctx = document.getElementById('marginChart').getContext('2d');
            
            // Create margin ranges
            const ranges = {
                'Excellent (70%+)': 0,
                'Good (50-70%)': 0,
                'Fair (30-50%)': 0,
                'Poor (<30%)': 0
            };

            menuItems.forEach(item => {
                const margin = item.profitMargin;
                if (margin >= 70) ranges['Excellent (70%+)']++;
                else if (margin >= 50) ranges['Good (50-70%)']++;
                else if (margin >= 30) ranges['Fair (30-50%)']++;
                else ranges['Poor (<30%)']++;
            });

            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: Object.keys(ranges),
                    datasets: [{
                        label: 'Number of Items',
                        data: Object.values(ranges),
                        backgroundColor: ['#00b894', '#74b9ff', '#feca57', '#e17055'],
                        borderColor: ['#00a085', '#0984e3', '#e1b12c', '#d63031'],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                stepSize: 1,
                                callback: function(value) {
                                    return value + ' items';
                                }
                            }
                        }
                    }
                }
            });
        }

        function generateCostChart() {
            const ctx = document.getElementById('costChart').getContext('2d');
            
            // Create scatter plot of cost vs price
            const data = menuItems.map(item => ({
                x: item.foodCost,
                y: item.sellingPrice,
                label: item.name,
                profit: item.sellingPrice - item.foodCost
            }));

            new Chart(ctx, {
                type: 'scatter',
                data: {
                    datasets: [{
                        label: 'Menu Items',
                        data: data,
                        backgroundColor: function(context) {
                            const profit = context.parsed.y - context.parsed.x;
                            const margin = (profit / context.parsed.y) * 100;
                            if (margin >= 60) return '#00b894';
                            if (margin >= 40) return '#74b9ff';
                            return '#e17055';
                        },
                        borderColor: '#fff',
                        borderWidth: 2,
                        pointRadius: 8,
                        pointHoverRadius: 10
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            callbacks: {
                                title: function(context) {
                                    return menuItems[context[0].dataIndex].name;
                                },
                                label: function(context) {
                                    const item = menuItems[context.dataIndex];
                                    const margin = ((item.sellingPrice - item.foodCost) / item.sellingPrice * 100).toFixed(1);
                                    return [
                                        'Food Cost: $' + context.parsed.x.toFixed(2),
                                        'Selling Price: $' + context.parsed.y.toFixed(2),
                                        'Profit Margin: ' + margin + '%'
                                    ];
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Food Cost ($)'
                            },
                            beginAtZero: true
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'Selling Price ($)'
                            },
                            beginAtZero: true
                        }
                    }
                }
            });
        }

        function showStatInfo(type) {
            const messages = {
                revenue: 'Total monthly revenue from all menu items based on current sales data and pricing.',
                items: 'Number of items currently on your menu. Consider optimal menu size for kitchen efficiency.',
                margin: 'Average profit margin across all menu items. Industry standard is 60-70% for food.',
                bestseller: 'Your highest selling item by volume. Consider promoting similar items or increasing capacity.'
            };
            alert(messages[type] || 'Statistical information about your menu performance.');
        }

        function showNotification(message, type) {
            const notification = document.createElement('div');
            notification.textContent = message;
            notification.style.cssText = `
                position: fixed; top: 20px; right: 20px;
                background: ${type === 'success' ? '#00b894' : type === 'warning' ? '#ffc107' : '#e17055'};
                color: white; padding: 15px 20px; border-radius: 10px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.3); z-index: 1001;
                font-weight: 600; max-width: 300px;
            `;
            document.body.appendChild(notification);
            setTimeout(() => notification.remove(), 4000);
        }
    </script>
</body>
</html>
"""

# Sample data and business logic
menu_items = []
analysis_history = []

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/menu-item', methods=['POST'])
def add_menu_item():
    """Add a new menu item"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'category', 'sellingPrice', 'foodCost', 'prepTime', 'monthlySales']
        for field in required_fields:
            if field not in data or data[field] == '':
                return jsonify({"error": f"Missing field: {field}"}), 400
        
        # Create menu item
        menu_item = {
            "id": len(menu_items) + 1,
            "name": data['name'],
            "category": data['category'],
            "sellingPrice": float(data['sellingPrice']),
            "foodCost": float(data['foodCost']),
            "prepTime": int(data['prepTime']),
            "monthlySales": int(data['monthlySales']),
            "ingredients": data.get('ingredients', []),
            "profitMargin": calculate_profit_margin(float(data['sellingPrice']), float(data['foodCost'])),
            "monthlyProfit": calculate_monthly_profit(float(data['sellingPrice']), float(data['foodCost']), int(data['monthlySales'])),
            "createdAt": datetime.now().isoformat()
        }
        
        menu_items.append(menu_item)
        
        return jsonify({
            "success": True,
            "menuItem": menu_item,
            "menuItems": menu_items
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/analysis/profit')
def profit_analysis():
    """Generate profit analysis recommendations"""
    if not menu_items:
        return jsonify({"recommendations": []})
    
    recommendations = []
    
    # Calculate overall metrics
    total_revenue = sum(item['sellingPrice'] * item['monthlySales'] for item in menu_items)
    total_profit = sum(item['monthlyProfit'] for item in menu_items)
    avg_margin = sum(item['profitMargin'] for item in menu_items) / len(menu_items)
    
    # High performers
    high_profit_items = sorted(menu_items, key=lambda x: x['monthlyProfit'], reverse=True)[:3]
    if high_profit_items:
        top_item = high_profit_items[0]
        recommendations.append({
            "title": f"Star Performer: {top_item['name']}",
            "description": f"This item generates ${top_item['monthlyProfit']:.2f} monthly profit with {top_item['profitMargin']:.1f}% margin. Consider featuring it prominently, training staff to upsell it, or creating similar items.",
            "type": ""
        })
    
    # Low performers
    low_profit_items = [item for item in menu_items if item['profitMargin'] < 30]
    if low_profit_items:
        worst_item = min(low_profit_items, key=lambda x: x['profitMargin'])
        recommendations.append({
            "title": f"Underperformer Alert: {worst_item['name']}",
            "description": f"Only {worst_item['profitMargin']:.1f}% margin (${worst_item['monthlyProfit']:.2f}/month). Consider increasing price by 15-20%, reducing portion size, or finding cheaper ingredients.",
            "type": "warning"
        })
    
    # Category analysis
    category_profits = {}
    for item in menu_items:
        cat = item['category']
        if cat not in category_profits:
            category_profits[cat] = {'profit': 0, 'count': 0}
        category_profits[cat]['profit'] += item['monthlyProfit']
        category_profits[cat]['count'] += 1
    
    best_category = max(category_profits.items(), key=lambda x: x[1]['profit'])
    recommendations.append({
        "title": f"Category Winner: {best_category[0]}",
        "description": f"Your {best_category[0].lower()} generate ${best_category[1]['profit']:.2f} monthly profit. Consider expanding this category with 2-3 similar items to capitalize on success.",
        "type": ""
    })
    
    # Overall health check
    if avg_margin > 65:
        recommendations.append({
            "title": "Excellent Profit Health",
            "description": f"Average margin of {avg_margin:.1f}% is above industry standard (60-70%). Focus on maintaining quality and consider strategic price increases on popular items.",
            "type": ""
        })
    elif avg_margin < 50:
        recommendations.append({
            "title": "Profit Margin Warning",
            "description": f"Average margin of {avg_margin:.1f}% is below recommended 60%. Review food costs, negotiate with suppliers, or adjust pricing across the menu.",
            "type": "danger"
        })
    
    return jsonify({"recommendations": recommendations})

@app.route('/api/analysis/pricing')
def pricing_optimization():
    """Generate pricing optimization recommendations"""
    if not menu_items:
        return jsonify({"recommendations": []})
    
    recommendations = []
    
    for item in menu_items:
        margin = item['profitMargin']
        current_price = item['sellingPrice']
        food_cost = item['foodCost']
        sales = item['monthlySales']
        
        # Price optimization suggestions
        if margin < 40:  # Very low margin
            target_price = food_cost / 0.6  # Target 60% margin
            price_increase = target_price - current_price
            recommendations.append({
                "title": f"Price Increase Needed: {item['name']}",
                "description": f"Current margin is only {margin:.1f}%. Increase price from ${current_price:.2f} to ${target_price:.2f} (+${price_increase:.2f}) to achieve 60% margin. Monitor sales impact.",
                "type": "warning"
            })
        
        elif margin > 80 and sales > 100:  # Very high margin with good sales
            suggested_decrease = current_price * 0.05  # 5% decrease
            new_price = current_price - suggested_decrease
            recommendations.append({
                "title": f"Price Optimization Opportunity: {item['name']}",
                "description": f"High margin ({margin:.1f}%) with strong sales ({sales} units). Consider reducing price by ${suggested_decrease:.2f} to ${new_price:.2f} to increase volume and competitiveness.",
                "type": ""
            })
        
        elif sales < 50:  # Low sales items
            if margin > 60:
                price_reduction = current_price * 0.1  # 10% reduction
                new_price = current_price - price_reduction
                recommendations.append({
                    "title": f"Volume Booster: {item['name']}",
                    "description": f"Low sales ({sales} units) despite good margin. Reduce price from ${current_price:.2f} to ${new_price:.2f} (-${price_reduction:.2f}) to stimulate demand.",
                    "type": ""
                })
            else:
                recommendations.append({
                    "title": f"Menu Review Required: {item['name']}",
                    "description": f"Low sales ({sales} units) and poor margin ({margin:.1f}%). Consider removing from menu or complete recipe/pricing overhaul.",
                    "type": "danger"
                })
    
    # Competitive pricing analysis
    category_prices = {}
    for item in menu_items:
        cat = item['category']
        if cat not in category_prices:
            category_prices[cat] = []
        category_prices[cat].append(item['sellingPrice'])
    
    for category, prices in category_prices.items():
        if len(prices) > 1:
            avg_price = sum(prices) / len(prices)
            max_price = max(prices)
            min_price = min(prices)
            
            if max_price > avg_price * 1.5:
                recommendations.append({
                    "title": f"Price Consistency Check: {category}",
                    "description": f"Large price variation in {category.lower()} (${min_price:.2f} - ${max_price:.2f}). Ensure pricing reflects value differences or consider adjustment.",
                    "type": "warning"
                })
    
    return jsonify({"recommendations": recommendations})

@app.route('/api/analysis/trends')
def trend_analysis():
    """Generate trend analysis recommendations"""
    if not menu_items:
        return jsonify({"recommendations": []})
    
    recommendations = []
    
    # Sales volume trends
    high_volume = [item for item in menu_items if item['monthlySales'] > 150]
    low_volume = [item for item in menu_items if item['monthlySales'] < 30]
    
    if high_volume:
        top_seller = max(high_volume, key=lambda x: x['monthlySales'])
        recommendations.append({
            "title": f"Trending Item: {top_seller['name']}",
            "description": f"Selling {top_seller['monthlySales']} units monthly. This high demand indicates strong customer preference. Consider creating variations or limited-time specials based on this item.",
            "type": ""
        })
    
    if low_volume:
        recommendations.append({
            "title": "Low Demand Items",
            "description": f"{len(low_volume)} items selling less than 30 units monthly. Review these for menu simplification, better promotion, or removal to focus kitchen resources on popular items.",
            "type": "warning"
        })
    
    # Category performance trends
    category_sales = {}
    for item in menu_items:
        cat = item['category']
        if cat not in category_sales:
            category_sales[cat] = 0
        category_sales[cat] += item['monthlySales']
    
    if category_sales:
        trending_category = max(category_sales.items(), key=lambda x: x[1])
        slow_category = min(category_sales.items(), key=lambda x: x[1])
        
        recommendations.append({
            "title": f"Category Trend: {trending_category[0]} Leading",
            "description": f"{trending_category[0]} selling {trending_category[1]} total units. Customer preference is clear - consider expanding this category with seasonal specials or premium options.",
            "type": ""
        })
        
        if slow_category[1] < trending_category[1] * 0.3:
            recommendations.append({
                "title": f"Category Decline: {slow_category[0]}",
                "description": f"{slow_category[0]} underperforming with only {slow_category[1]} units. Consider refreshing recipes, adjusting presentation, or seasonal repositioning.",
                "type": "warning"
            })
    
    # Prep time efficiency trends
    quick_items = [item for item in menu_items if item['prepTime'] <= 10]
    slow_items = [item for item in menu_items if item['prepTime'] > 20]
    
    if quick_items and slow_items:
        avg_quick_sales = sum(item['monthlySales'] for item in quick_items) / len(quick_items)
        avg_slow_sales = sum(item['monthlySales'] for item in slow_items) / len(slow_items)
        
        if avg_quick_sales > avg_slow_sales * 1.2:
            recommendations.append({
                "title": "Kitchen Efficiency Trend",
                "description": f"Quick-prep items (≤10 min) outselling complex items by {((avg_quick_sales/avg_slow_sales-1)*100):.0f}%. Focus on streamlined recipes and consider simplifying high-prep items.",
                "type": ""
            })
    
    # Profit per minute analysis
    for item in menu_items:
        profit_per_minute = (item['sellingPrice'] - item['foodCost']) / item['prepTime']
        item['efficiency_score'] = profit_per_minute
    
    most_efficient = max(menu_items, key=lambda x: x['efficiency_score'])
    recommendations.append({
        "title": f"Efficiency Champion: {most_efficient['name']}",
        "description": f"Generates ${most_efficient['efficiency_score']:.2f} profit per minute of prep time. This efficiency model should guide future menu development and staff training priorities.",
        "type": ""
    })
    
    return jsonify({"recommendations": recommendations})

@app.route('/api/analysis/costs')
def cost_analysis():
    """Generate cost analysis recommendations"""
    if not menu_items:
        return jsonify({"recommendations": []})
    
    recommendations = []
    
    # Food cost percentage analysis
    total_revenue = sum(item['sellingPrice'] * item['monthlySales'] for item in menu_items)
    total_food_cost = sum(item['foodCost'] * item['monthlySales'] for item in menu_items)
    overall_food_cost_percentage = (total_food_cost / total_revenue) * 100
    
    recommendations.append({
        "title": f"Overall Food Cost: {overall_food_cost_percentage:.1f}%",
        "description": f"Industry target is 28-35%. {'Excellent cost control!' if overall_food_cost_percentage < 30 else 'Good range' if overall_food_cost_percentage < 35 else 'Above target - review supplier costs and portion sizes'}",
        "type": "" if overall_food_cost_percentage < 35 else "warning"
    })
    
    # High food cost items
    high_cost_items = [item for item in menu_items if (item['foodCost'] / item['sellingPrice']) > 0.4]
    if high_cost_items:
        worst_cost_item = max(high_cost_items, key=lambda x: x['foodCost'] / x['sellingPrice'])
        cost_percentage = (worst_cost_item['foodCost'] / worst_cost_item['sellingPrice']) * 100
        recommendations.append({
            "title": f"High Food Cost Alert: {worst_cost_item['name']}",
            "description": f"Food cost is {cost_percentage:.1f}% of selling price. Consider negotiating with suppliers, reducing portion size by 10-15%, or finding substitute ingredients.",
            "type": "danger"
        })
    
    # Ingredient cost optimization
    all_ingredients = []
    for item in menu_items:
        all_ingredients.extend(item.get('ingredients', []))
    
    # Count ingredient frequency
    ingredient_frequency = {}
    for ingredient in all_ingredients:
        ingredient = ingredient.strip().lower()
        if ingredient:
            ingredient_frequency[ingredient] = ingredient_frequency.get(ingredient, 0) + 1
    
    if ingredient_frequency:
        most_used = max(ingredient_frequency.items(), key=lambda x: x[1])
        recommendations.append({
            "title": f"Bulk Purchase Opportunity: {most_used[0].title()}",
            "description": f"Used in {most_used[1]} different menu items. Negotiate volume discounts with suppliers or consider buying in larger quantities to reduce per-unit cost.",
            "type": ""
        })
    
    # Labor cost implications (prep time analysis)
    labor_intensive_items = sorted(menu_items, key=lambda x: x['prepTime'], reverse=True)[:3]
    if labor_intensive_items:
        most_intensive = labor_intensive_items[0]
        if most_intensive['prepTime'] > 30:
            recommendations.append({
                "title": f"Labor Cost Concern: {most_intensive['name']}",
                "description": f"{most_intensive['prepTime']} minutes prep time significantly impacts labor costs. Consider pre-prep strategies, simplifying recipe, or pricing adjustment to account for labor investment.",
                "type": "warning"
            })
    
    # Seasonal cost considerations
    recommendations.append({
        "title": "Seasonal Cost Planning",
        "description": "Review your menu quarterly for seasonal ingredient price fluctuations. Consider featuring seasonal specials when ingredients are at peak freshness and lowest cost.",
        "type": ""
    })
    
    # Waste reduction opportunities
    single_use_ingredients = []
    for item in menu_items:
        for ingredient in item.get('ingredients', []):
            ingredient = ingredient.strip().lower()
            if ingredient and ingredient_frequency.get(ingredient, 0) == 1:
                single_use_ingredients.append(ingredient)
    
    if len(single_use_ingredients) > 3:
        recommendations.append({
            "title": "Ingredient Utilization",
            "description": f"{len(single_use_ingredients)} ingredients used in only one dish. Cross-utilize ingredients across multiple menu items to reduce waste and inventory costs.",
            "type": "warning"
        })
    
    return jsonify({"recommendations": recommendations})

def calculate_profit_margin(selling_price, food_cost):
    """Calculate profit margin percentage"""
    if selling_price == 0:
        return 0
    return ((selling_price - food_cost) / selling_price) * 100

def calculate_monthly_profit(selling_price, food_cost, monthly_sales):
    """Calculate monthly profit"""
    return (selling_price - food_cost) * monthly_sales

def open_browser():
    """Open browser after delay"""
    time.sleep(3)
    webbrowser.open('http://localhost:5000')

if __name__ == '__main__':
    print("🍽️  Restaurant Menu Optimizer")
    print("=" * 40)
    print("✅ AI-powered menu analysis and optimization")
    print("🌐 Starting server at http://localhost:5000")
    print("\nFeatures:")
    print("  • Menu profitability analysis")
    print("  • Dynamic pricing optimization")
    print("  • Cost control recommendations")
    print("  • Sales trend identification")
    print("  • Kitchen efficiency metrics")
    print("\nPress Ctrl+C to stop")
    print("-" * 40)
    
    # Auto-open browser
    Timer(2.0, open_browser).start()
    
    try:
        app.run(debug=False, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Restaurant Menu Optimizer stopped successfully")