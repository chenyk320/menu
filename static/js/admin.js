// 全局变量
let dishesData = [];
let categoriesData = [];
let allergensData = [];

// 初始化页面
document.addEventListener('DOMContentLoaded', function() {
    loadData();
    setupEventListeners();
});

// 加载数据
async function loadData() {
    try {
        const [dishesResponse, categoriesResponse, allergensResponse] = await Promise.all([
            fetch('/api/dishes'),
            fetch('/api/categories'),
            fetch('/api/allergens')
        ]);

        dishesData = await dishesResponse.json();
        categoriesData = await categoriesResponse.json();
        allergensData = await allergensResponse.json();

        renderAllData();
    } catch (error) {
        console.error('加载数据失败:', error);
        showError('加载数据失败，请刷新页面重试');
    }
}

// 设置事件监听器
function setupEventListeners() {
    // 导航切换
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            switchTab(this.dataset.tab);
        });
    });

    // 添加按钮
    document.getElementById('add-dish-btn').addEventListener('click', () => openModal('dish-modal'));
    document.getElementById('add-category-btn').addEventListener('click', () => openModal('category-modal'));
    document.getElementById('add-allergen-btn').addEventListener('click', () => openModal('allergen-modal'));

    // 表单提交
    document.getElementById('dish-form').addEventListener('submit', handleDishSubmit);
    document.getElementById('edit-dish-form').addEventListener('submit', handleEditDishSubmit);
    document.getElementById('category-form').addEventListener('submit', handleCategorySubmit);
    document.getElementById('allergen-form').addEventListener('submit', handleAllergenSubmit);

    // 模态框点击外部关闭
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                closeModal(this.id);
            }
        });
    });
}

// 切换标签页
function switchTab(tabName) {
    // 更新导航按钮状态
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.tab === tabName) {
            btn.classList.add('active');
        }
    });

    // 更新内容区域
    document.querySelectorAll('.admin-section').forEach(section => {
        section.classList.remove('active');
        if (section.id === `${tabName}-section`) {
            section.classList.add('active');
        }
    });
}

// 渲染所有数据
function renderAllData() {
    renderDishes();
    renderCategories();
    renderAllergens();
    populateCategorySelect();
    populateAllergenCheckboxes();
}

// 处理图片加载失败
function handleImageError(img) {
    img.style.display = 'none';
    // 创建一个占位符div
    const placeholder = document.createElement('div');
    placeholder.className = 'dish-image-placeholder';
    placeholder.innerHTML = '📷';
    placeholder.style.cssText = `
        width: 100%;
        height: 200px;
        background: #f8f9fa;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        color: #6c757d;
        border-radius: 8px;
    `;
    img.parentNode.insertBefore(placeholder, img);
}

// 渲染菜品列表
function renderDishes() {
    const dishesList = document.getElementById('dishes-list');
    
    if (dishesData.length === 0) {
        dishesList.innerHTML = '<div class="loading">暂无菜品数据</div>';
        return;
    }

    dishesList.innerHTML = dishesData.map(dish => {
        const imageSrc = dish.image ? '/static/' + dish.image : '/static/images/placeholder.svg';
        return `
        <div class="item-card dish-card">
            <img src="${imageSrc}" 
                 alt="${dish.name_cn}" class="dish-image" 
                 onerror="handleImageError(this);">
            <div class="dish-info">
                <div class="dish-number">${dish.dish_number}</div>
                <div class="dish-price">€${dish.price.toFixed(2)}</div>
                <div class="dish-names">
                    <div class="dish-name">${dish.name_cn}</div>
                    <div class="dish-name" style="color: #6c757d; font-size: 1rem;">${dish.name_it}</div>
                </div>
                ${dish.description_it ? `<div class="dish-description">${dish.description_it}</div>` : ''}
                <div class="dish-allergens">
                    ${dish.allergens.map(allergen => 
                        `<div class="allergen-badge" title="${allergen.name_cn}" style="background-image: url('/static/${allergen.icon}')"></div>`
                    ).join('')}
                </div>
                <div class="dish-actions">
                    <button class="edit-btn" onclick="editDish(${dish.id})">编辑</button>
                    <button class="delete-btn" onclick="deleteDish(${dish.id})">删除</button>
                </div>
            </div>
        </div>
        `;
    }).join('');
}

// 渲染分类列表
function renderCategories() {
    const categoriesList = document.getElementById('categories-list');
    
    if (categoriesData.length === 0) {
        categoriesList.innerHTML = '<div class="loading">暂无分类数据</div>';
        return;
    }

    categoriesList.innerHTML = categoriesData.map(category => `
        <div class="item-card">
            <div class="item-header">
                <div class="item-title">${category.prefix_letter} - ${category.name_cn} / ${category.name_it}</div>
                <button class="delete-btn" onclick="deleteCategory(${category.id})">删除</button>
            </div>
            <div class="item-content">
                排序: ${category.sort_order} | 前缀字母: ${category.prefix_letter}
            </div>
        </div>
    `).join('');
}

// 渲染过敏源列表
function renderAllergens() {
    const allergensList = document.getElementById('allergens-list');
    
    if (allergensData.length === 0) {
        allergensList.innerHTML = '<div class="loading">暂无过敏源数据</div>';
        return;
    }

    allergensList.innerHTML = allergensData.map(allergen => `
        <div class="item-card">
            <div class="item-header">
                <div class="item-title">
                    <span style="font-size: 1.5rem; margin-right: 10px;">${getAllergenIcon(allergen.icon)}</span>
                    ${allergen.name_cn} / ${allergen.name_it}
                </div>
                <button class="delete-btn" onclick="deleteAllergen(${allergen.id})">删除</button>
            </div>
            <div class="item-content">
                ${allergen.description_cn ? `<div>中文描述: ${allergen.description_cn}</div>` : ''}
                ${allergen.description_it ? `<div>意大利语描述: ${allergen.description_it}</div>` : ''}
            </div>
        </div>
    `).join('');
}

// 填充分类选择框
function populateCategorySelect() {
    const categorySelect = document.getElementById('category_id');
    categorySelect.innerHTML = '<option value="">选择分类</option>';
    
    categoriesData.forEach(category => {
        const option = document.createElement('option');
        option.value = category.id;
        option.textContent = `${category.prefix_letter} - ${category.name_cn} / ${category.name_it}`;
        categorySelect.appendChild(option);
    });
}

// 填充过敏源复选框
function populateAllergenCheckboxes() {
    const allergenCheckboxes = document.getElementById('allergen-checkboxes');
    allergenCheckboxes.innerHTML = '';
    
    allergensData.forEach(allergen => {
        const checkboxDiv = document.createElement('div');
        checkboxDiv.className = 'allergen-checkbox';
        checkboxDiv.innerHTML = `
            <input type="checkbox" id="allergen_${allergen.id}" name="allergens" value="${allergen.id}">
            <label for="allergen_${allergen.id}">
                <span style="font-size: 1.2rem; margin-right: 8px;">${getAllergenIcon(allergen.icon)}</span>
                ${allergen.name_cn}
            </label>
        `;
        allergenCheckboxes.appendChild(checkboxDiv);
    });
}

// 打开模态框
function openModal(modalId) {
    document.getElementById(modalId).style.display = 'block';
    document.body.style.overflow = 'hidden';
}

// 关闭模态框
function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
    document.body.style.overflow = 'auto';
    
    // 清空表单
    const form = document.querySelector(`#${modalId} form`);
    if (form) {
        form.reset();
    }
}

// 处理菜品表单提交
async function handleDishSubmit(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    
    try {
        const response = await fetch('/api/dish', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            showSuccess('菜品添加成功！');
            closeModal('dish-modal');
            loadData(); // 重新加载数据
        } else {
            showError(result.message || '添加菜品失败');
        }
    } catch (error) {
        console.error('添加菜品失败:', error);
        showError('添加菜品失败，请重试');
    }
}

// 编辑菜品
function editDish(dishId) {
    const dish = dishesData.find(d => d.id === dishId);
    if (!dish) {
        showError('菜品不存在');
        return;
    }
    
    // 填充表单数据
    document.getElementById('edit-dish-id').value = dish.id;
    document.getElementById('edit-name_cn').value = dish.name_cn;
    document.getElementById('edit-name_it').value = dish.name_it;
    document.getElementById('edit-description_it').value = dish.description_it || '';
    document.getElementById('edit-price').value = dish.price;
    document.getElementById('edit-category_id').value = dish.category_id || '';
    document.getElementById('edit-surgelato').checked = dish.surgelato || false;
    
    // 显示当前图片
    const currentImagePreview = document.getElementById('current-image-preview');
    const deleteImageBtn = document.getElementById('delete-image-btn');
    if (dish.image) {
        currentImagePreview.innerHTML = `
            <div>当前图片:</div>
            <img src="/static/${dish.image}" alt="当前图片">
        `;
        deleteImageBtn.style.display = 'block';
        deleteImageBtn.onclick = () => deleteDishImage(dish.id);
    } else {
        currentImagePreview.innerHTML = '<div class="no-image">暂无图片</div>';
        deleteImageBtn.style.display = 'none';
    }
    
    // 填充分类选择框
    const editCategorySelect = document.getElementById('edit-category_id');
    editCategorySelect.innerHTML = '<option value="">选择分类</option>';
    categoriesData.forEach(category => {
        const option = document.createElement('option');
        option.value = category.id;
        option.textContent = `${category.prefix_letter} - ${category.name_cn} / ${category.name_it}`;
        if (category.id === dish.category_id) {
            option.selected = true;
        }
        editCategorySelect.appendChild(option);
    });
    
    // 填充过敏源复选框
    const editAllergenCheckboxes = document.getElementById('edit-allergen-checkboxes');
    editAllergenCheckboxes.innerHTML = '';
    allergensData.forEach(allergen => {
        const checkboxDiv = document.createElement('div');
        checkboxDiv.className = 'allergen-checkbox';
        const isChecked = dish.allergens.some(a => a.id === allergen.id);
        checkboxDiv.innerHTML = `
            <input type="checkbox" id="edit-allergen_${allergen.id}" name="allergens" value="${allergen.id}" ${isChecked ? 'checked' : ''}>
            <label for="edit-allergen_${allergen.id}">
                <span style="font-size: 1.2rem; margin-right: 8px;">${getAllergenIcon(allergen.icon)}</span>
                ${allergen.name_cn}
            </label>
        `;
        editAllergenCheckboxes.appendChild(checkboxDiv);
    });
    
    // 打开编辑模态框
    openModal('edit-dish-modal');
}

// 处理编辑菜品表单提交
async function handleEditDishSubmit(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const dishId = formData.get('dish_id');
    
    try {
        const response = await fetch(`/api/dish/${dishId}`, {
            method: 'PUT',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            showSuccess('菜品更新成功！');
            closeModal('edit-dish-modal');
            loadData(); // 重新加载数据
        } else {
            showError(result.message || '更新菜品失败');
        }
    } catch (error) {
        console.error('更新菜品失败:', error);
        showError('更新菜品失败，请重试');
    }
}

// 处理分类表单提交
async function handleCategorySubmit(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());
    
    try {
        const response = await fetch('/api/category', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showSuccess('分类添加成功！');
            closeModal('category-modal');
            loadData(); // 重新加载数据
        } else {
            showError(result.message || '添加分类失败');
        }
    } catch (error) {
        console.error('添加分类失败:', error);
        showError('添加分类失败，请重试');
    }
}

// 处理过敏源表单提交
async function handleAllergenSubmit(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());
    
    try {
        const response = await fetch('/api/allergen', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showSuccess('过敏源添加成功！');
            closeModal('allergen-modal');
            loadData(); // 重新加载数据
        } else {
            showError(result.message || '添加过敏源失败');
        }
    } catch (error) {
        console.error('添加过敏源失败:', error);
        showError('添加过敏源失败，请重试');
    }
}

// 删除菜品
async function deleteDish(dishId) {
    if (!confirm('确定要删除这个菜品吗？')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/dish/${dishId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showSuccess('菜品删除成功！');
            loadData(); // 重新加载数据
        } else {
            showError(result.message || '删除菜品失败');
        }
    } catch (error) {
        console.error('删除菜品失败:', error);
        showError('删除菜品失败，请重试');
    }
}

// 删除分类
async function deleteCategory(categoryId) {
    if (!confirm('确定要删除这个分类吗？')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/category/${categoryId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showSuccess('分类删除成功！');
            loadData(); // 重新加载数据
        } else {
            showError(result.message || '删除分类失败');
        }
    } catch (error) {
        console.error('删除分类失败:', error);
        showError('删除分类失败，请重试');
    }
}

// 删除过敏源
async function deleteAllergen(allergenId) {
    if (!confirm('确定要删除这个过敏源吗？')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/allergen/${allergenId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showSuccess('过敏源删除成功！');
            loadData(); // 重新加载数据
        } else {
            showError(result.message || '删除过敏源失败');
        }
    } catch (error) {
        console.error('删除过敏源失败:', error);
        showError('删除过敏源失败，请重试');
    }
}

// 删除菜品图片
async function deleteDishImage(dishId) {
    if (!confirm('确定要删除这个菜品的图片吗？')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/dish/${dishId}/image`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showSuccess('图片删除成功！');
            // 更新当前图片预览
            const currentImagePreview = document.getElementById('current-image-preview');
            const deleteImageBtn = document.getElementById('delete-image-btn');
            currentImagePreview.innerHTML = '<div class="no-image">暂无图片</div>';
            deleteImageBtn.style.display = 'none';
            // 重新加载数据以更新菜品列表
            loadData();
        } else {
            showError(result.message || '删除图片失败');
        }
    } catch (error) {
        console.error('删除图片失败:', error);
        showError('删除图片失败，请重试');
    }
}

// 获取过敏源图标
function getAllergenIcon(iconString) {
    if (iconString && iconString.length <= 4) {
        return iconString;
    }
    return '?';
}

// 显示成功消息
function showSuccess(message) {
    // 创建成功提示
    const successDiv = document.createElement('div');
    successDiv.className = 'success-message';
    successDiv.textContent = message;
    successDiv.style.position = 'fixed';
    successDiv.style.top = '20px';
    successDiv.style.right = '20px';
    successDiv.style.zIndex = '10000';
    successDiv.style.maxWidth = '300px';
    
    document.body.appendChild(successDiv);
    
    // 3秒后自动移除
    setTimeout(() => {
        if (successDiv.parentNode) {
            successDiv.parentNode.removeChild(successDiv);
        }
    }, 3000);
}

// 显示错误消息
function showError(message) {
    // 创建错误提示
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    errorDiv.style.position = 'fixed';
    errorDiv.style.top = '20px';
    errorDiv.style.right = '20px';
    errorDiv.style.zIndex = '10000';
    errorDiv.style.maxWidth = '300px';
    
    document.body.appendChild(errorDiv);
    
    // 5秒后自动移除
    setTimeout(() => {
        if (errorDiv.parentNode) {
            errorDiv.parentNode.removeChild(errorDiv);
        }
    }, 5000);
}