// 全局变量
let currentLanguage = 'cn';
let currentCategory = 'all';
let dishesData = [];
let categoriesData = [];
let allergensData = [];

// 立即执行的测试
console.log('JavaScript文件已加载');

// 测试语言按钮是否存在
setTimeout(function() {
    const langButtons = document.querySelectorAll('.lang-btn');
    console.log('找到语言按钮数量:', langButtons.length);
    langButtons.forEach((btn, index) => {
        console.log(`按钮 ${index}:`, btn.textContent, btn.dataset.lang);
    });
}, 1000);

// 初始化页面
document.addEventListener('DOMContentLoaded', function() {
    console.log('页面加载完成，开始初始化...');
    setupEventListeners();
    loadData();
});

// 加载数据
async function loadData() {
    console.log('开始加载数据...');
    
    // 显示加载状态
    showLoadingState();
    
    try {
        const [dishesResponse, categoriesResponse, allergensResponse] = await Promise.all([
            fetch('/api/dishes'),
            fetch('/api/categories'),
            fetch('/api/allergens')
        ]);

        dishesData = await dishesResponse.json();
        categoriesData = await categoriesResponse.json();
        allergensData = await allergensResponse.json();

        console.log('数据加载完成，开始渲染...');
        hideLoadingState();
        renderAllergenInfo();
        renderCategoryNav();
        renderDishes();
        console.log('渲染完成');
    } catch (error) {
        console.error('加载数据失败:', error);
        hideLoadingState();
        showError('加载菜单数据失败，请刷新页面重试');
    }
}

// 显示加载状态
function showLoadingState() {
    const dishesGrid = document.getElementById('dishes-grid');
    dishesGrid.innerHTML = `
        <div class="loading-container" style="grid-column: 1 / -1; text-align: center; padding: 50px;">
            <div class="loading-spinner"></div>
            <p class="loading-text">${currentLanguage === 'cn' ? '正在加载菜单...' : 'Caricamento menu...'}</p>
        </div>
    `;
}

// 隐藏加载状态
function hideLoadingState() {
    const loadingContainer = document.querySelector('.loading-container');
    if (loadingContainer) {
        loadingContainer.remove();
    }
}

// 设置事件监听器
function setupEventListeners() {
    console.log('设置事件监听器...');
    
    // 统一的事件委托处理
    document.addEventListener('click', function(e) {
        console.log('点击事件触发，目标元素:', e.target);
        console.log('目标元素类名:', e.target.classList);
        
        if (e.target.classList.contains('lang-btn')) {
            console.log('语言按钮被点击:', e.target.dataset.lang);
            switchLanguage(e.target.dataset.lang);
        } else if (e.target.classList.contains('category-btn')) {
            console.log('分类按钮被点击:', e.target.dataset.category);
            switchCategory(e.target.dataset.category);
        }
    });
    
    console.log('事件监听器设置完成');
}

// 切换语言
function switchLanguage(lang) {
    console.log('切换语言到:', lang);
    currentLanguage = lang;
    
    // 更新语言按钮状态
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.lang === lang) {
            btn.classList.add('active');
        }
    });

    // 显示/隐藏订购说明（仅意大利语显示）
    const orderInstruction = document.getElementById('order-instruction');
    if (orderInstruction) {
        orderInstruction.style.display = lang === 'it' ? 'block' : 'none';
    }

    console.log('开始重新渲染内容...');
    // 重新渲染所有内容
    renderAllergenInfo();
    renderCategoryNav();
    renderDishes();
    console.log('内容渲染完成');
}

// 切换分类
function switchCategory(category) {
    currentCategory = category;
    
    // 更新分类按钮状态
    document.querySelectorAll('.category-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.category === category) {
            btn.classList.add('active');
        }
    });

    renderDishes();
}

// 切换过敏源信息显示
function toggleAllergenInfo() {
    const content = document.getElementById('allergen-content');
    const toggle = document.getElementById('allergen-toggle');
    
    if (content.style.display === 'none') {
        content.style.display = 'block';
        toggle.classList.add('rotated');
    } else {
        content.style.display = 'none';
        toggle.classList.remove('rotated');
    }
}

// 渲染过敏源信息
function renderAllergenInfo() {
    const allergenGrid = document.getElementById('allergen-grid');
    const allergenTitle = document.querySelector('.allergen-title');
    
    // 更新标题
    allergenTitle.textContent = allergenTitle.dataset[currentLanguage];
    
    // 清空并重新渲染过敏源网格
    allergenGrid.innerHTML = '';
    
    allergensData.forEach(allergen => {
        const allergenItem = document.createElement('div');
        allergenItem.className = 'allergen-item';
        allergenItem.innerHTML = `
            <div class="allergen-icon" style="background-image: url('/static/${allergen.icon}')"></div>
            <div class="allergen-name">${allergen[`name_${currentLanguage}`]}</div>
        `;
        allergenGrid.appendChild(allergenItem);
    });
}

// 渲染分类导航
function renderCategoryNav() {
    const categoryNav = document.getElementById('category-nav');
    
    // 清空所有按钮
    categoryNav.innerHTML = '';
    
    // 添加"全部"按钮
    const allBtn = document.createElement('button');
    allBtn.className = 'category-btn active';
    allBtn.dataset.category = 'all';
    allBtn.dataset.cn = '全部';
    allBtn.dataset.it = 'Tutti';
    allBtn.textContent = currentLanguage === 'cn' ? '全部' : 'Tutti';
    categoryNav.appendChild(allBtn);
    
    // 添加"新菜"按钮
    const newBtn = document.createElement('button');
    newBtn.className = 'category-btn';
    newBtn.dataset.category = 'new';
    newBtn.dataset.cn = '新菜';
    newBtn.dataset.it = 'Novità';
    newBtn.textContent = currentLanguage === 'cn' ? '新菜' : 'Novità';
    categoryNav.appendChild(newBtn);
    
    // 添加分类按钮
    categoriesData.forEach(category => {
        const categoryBtn = document.createElement('button');
        categoryBtn.className = 'category-btn';
        categoryBtn.dataset.category = category.id;
        categoryBtn.dataset.cn = category.name_cn;
        categoryBtn.dataset.it = category.name_it;
        categoryBtn.textContent = category[`name_${currentLanguage}`];
        categoryNav.appendChild(categoryBtn);
    });
}


// 创建菜品卡片
function createDishCard(dish) {
    const card = document.createElement('div');
    card.className = 'dish-card';
    
    // 构建图片HTML - 使用懒加载
    const imageHtml = dish.image 
        ? `<img data-src="/static/${dish.image}" alt="${dish[`name_${currentLanguage}`]}" class="dish-image lazy-load" src="/static/images/placeholder.jpg">`
        : `<div class="dish-image" style="display: flex; align-items: center; justify-content: center; background: #f8f9fa; color: #6c757d;">📷</div>`;
    
    // 构建过敏源徽章HTML
    const allergenBadges = dish.allergens.map(allergen => 
        `<div class="allergen-badge" title="${allergen[`name_${currentLanguage}`]}">
            <img src="/static/${allergen.icon}" alt="${allergen[`name_${currentLanguage}`]}" style="width: 100%; height: 100%; object-fit: contain;">
        </div>`
    ).join('');
    
    // 构建surgelato标识（仅意大利语显示）
    const surgelatoBadge = dish.surgelato && currentLanguage === 'it' 
        ? `<div class="surgelato-badge">❄️ Surgelato</div>` 
        : '';
    
    // 构建人气菜标识
    const popularBadge = dish.is_popular 
        ? `<div class="popular-badge">${currentLanguage === 'cn' ? '🔥 热销' : '🔥 Hot'}</div>` 
        : '';
    
    // 构建新菜标识
    const newBadge = dish.is_new 
        ? `<div class="new-badge">${currentLanguage === 'cn' ? '✨ 新品' : '✨ New'}</div>` 
        : '';
    
    // 构建价格HTML
    let priceHtml = '';
    if (dish.portions && dish.portions.length > 0) {
        // 如果有分量，显示分量价格
        const portionsHtml = dish.portions.map(portion => 
            `<div class="portion-item">
                <span class="portion-name">${portion[`name_${currentLanguage}`]}</span>
                <span class="portion-price">€${portion.price.toFixed(2)}</span>
            </div>`
        ).join('');
        priceHtml = `<div class="dish-portions">${portionsHtml}</div>`;
    } else {
        // 如果没有分量，显示默认价格
        priceHtml = `<div class="dish-price">€${dish.price.toFixed(2)}</div>`;
    }
    
    card.innerHTML = `
        ${imageHtml}
        <div class="dish-content">
            <div class="dish-header">
                <span class="dish-number">${dish.dish_number}</span>
            </div>
            <h3 class="dish-name">${dish[`name_${currentLanguage}`]}</h3>
            ${dish.description_it && currentLanguage === 'it' ? `<p class="dish-description">${dish.description_it}</p>` : ''}
            ${priceHtml}
            ${popularBadge}
            ${newBadge}
            ${surgelatoBadge}
            ${dish.allergens.length > 0 ? `<div class="dish-allergens">${allergenBadges}</div>` : ''}
        </div>
    `;
    
    return card;
}

// 获取过敏源图标 - 已废弃，现在使用背景图片
function getAllergenIcon(iconString) {
    // 这个函数已不再使用，现在直接使用背景图片
    return '';
}

// 显示错误信息
function showError(message) {
    const dishesGrid = document.getElementById('dishes-grid');
    dishesGrid.innerHTML = `
        <div class="error-message" style="grid-column: 1 / -1; text-align: center; padding: 50px; color: #e74c3c;">
            <p>${message}</p>
        </div>
    `;
}

// 获取当前语言
function getCurrentLanguage() {
    return currentLanguage;
}

// 获取当前分类
function getCurrentCategory() {
    return currentCategory;
}

// 懒加载功能
function initLazyLoading() {
    const lazyImages = document.querySelectorAll('.lazy-load');
    
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy-load');
                    img.classList.add('loaded');
                    imageObserver.unobserve(img);
                }
            });
        }, {
            rootMargin: '50px 0px', // 提前50px开始加载
            threshold: 0.1
        });
        
        lazyImages.forEach(img => imageObserver.observe(img));
    } else {
        // 降级处理：直接加载所有图片
        lazyImages.forEach(img => {
            img.src = img.dataset.src;
            img.classList.remove('lazy-load');
            img.classList.add('loaded');
        });
    }
}

// 在渲染菜品后初始化懒加载
function renderDishes() {
    const dishesGrid = document.getElementById('dishes-grid');
    
    // 过滤菜品
    let filteredDishes = dishesData;
    if (currentCategory === 'new') {
        // 显示所有新菜
        filteredDishes = dishesData.filter(dish => dish.is_new);
    } else if (currentCategory !== 'all') {
        // 显示指定分类的菜品
        filteredDishes = dishesData.filter(dish => dish.category_id == currentCategory);
    }
    
    // 清空网格
    dishesGrid.innerHTML = '';
    
    if (filteredDishes.length === 0) {
        dishesGrid.innerHTML = `
            <div class="no-dishes">
                <p>${currentLanguage === 'cn' ? '暂无菜品' : 'Nessun piatto disponibile'}</p>
            </div>
        `;
        return;
    }
    
    // 渲染菜品卡片
    filteredDishes.forEach(dish => {
        const dishCard = createDishCard(dish);
        dishesGrid.appendChild(dishCard);
    });
    
    // 初始化懒加载
    setTimeout(() => {
        initLazyLoading();
    }, 100);
}