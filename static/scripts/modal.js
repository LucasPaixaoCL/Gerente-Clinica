// REMOVIDO: toggle tema (btn + localStorage)

// modal lançamentos
const editModal = document.getElementById('editModal');
const editId = document.getElementById('editId');
const editDate = document.getElementById('editDate');
const editKind = document.getElementById('editKind');
const editCategory = document.getElementById('editCategory');
const editDescription = document.getElementById('editDescription');
const editAmount = document.getElementById('editAmount');

function openEditModal(button) {
    const { id, date, kind, category, description, amount } = button.dataset;
    editId.value = id;
    editDate.value = date;
    editKind.value = kind;
    editCategory.value = category;
    editDescription.value = description;
    editAmount.value = (amount || '').toString().replace(',', '.');

    editModal.classList.remove('hidden');
    editModal.classList.add('flex');
}

function closeEditModal() {
    editModal.classList.add('hidden');
    editModal.classList.remove('flex');
}

// modal cliente
const clienteModal = document.getElementById('clienteModal');
const clienteId = document.getElementById('clienteId');
const clienteNome = document.getElementById('clienteNome');
const clienteTelefone = document.getElementById('clienteTelefone');
const clienteEmail = document.getElementById('clienteEmail');
// hidden para excluir
const clienteDeleteId = document.getElementById('clienteDeleteId');

function openClienteModal(button) {
    const { id, nome, telefone, email } = button.dataset;

    clienteId.value = id;
    if (clienteDeleteId) clienteDeleteId.value = id;

    clienteNome.value = nome || '';
    clienteTelefone.value = telefone || '';
    clienteEmail.value = email || '';

    clienteModal.classList.remove('hidden');
    clienteModal.classList.add('flex');
}

function closeClienteModal() {
    clienteModal.classList.add('hidden');
    clienteModal.classList.remove('flex');
}

// modal produto
const produtoModal = document.getElementById('produtoModal');
const produtoId = document.getElementById('produtoId');
const produtoNome = document.getElementById('produtoNome');
const produtoPreco = document.getElementById('produtoPreco');
const produtoEstoque = document.getElementById('produtoEstoque');
// hidden para excluir
const produtoDeleteId = document.getElementById('produtoDeleteId');

function openProdutoModal(button) {
    const { id, nome, preco, estoque } = button.dataset;

    produtoId.value = id;
    if (produtoDeleteId) produtoDeleteId.value = id;

    produtoNome.value = nome || '';
    produtoPreco.value = (preco || '').toString().replace(',', '.');
    produtoEstoque.value = estoque || 0;

    produtoModal.classList.remove('hidden');
    produtoModal.classList.add('flex');
}

function closeProdutoModal() {
    produtoModal.classList.add('hidden');
    produtoModal.classList.remove('flex');
}

// fechar modais com ESC ou clique fora
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        if (!editModal.classList.contains('hidden')) closeEditModal();
        if (!clienteModal.classList.contains('hidden')) closeClienteModal();
        if (!produtoModal.classList.contains('hidden')) closeProdutoModal();
    }
});

[editModal, clienteModal, produtoModal].forEach(modal => {
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            if (modal === editModal) closeEditModal();
            if (modal === clienteModal) closeClienteModal();
            if (modal === produtoModal) closeProdutoModal();
        }
    });
});


// ===== TOAST DE CONFIRMAÇÃO DE EXCLUSÃO =====
let pendingDeleteForm = null;

function openDeleteToast(message, form) {
    pendingDeleteForm = form || null;

    const toast = document.getElementById('toastConfirm');
    const msgEl = document.getElementById('toastMessage');

    if (msgEl && message) {
        msgEl.textContent = message;
    }

    if (toast) {
        toast.classList.remove('hidden');
    }

    // impede o submit padrão do form
    return false;
}

function cancelDeleteToast() {
    const toast = document.getElementById('toastConfirm');
    if (toast) {
        toast.classList.add('hidden');
    }
    pendingDeleteForm = null;
}

function confirmDeleteToast() {
    const toast = document.getElementById('toastConfirm');
    if (toast) {
        toast.classList.add('hidden');
    }

    if (pendingDeleteForm) {
        // envia o form de fato
        pendingDeleteForm.submit();
        pendingDeleteForm = null;
    }
}
