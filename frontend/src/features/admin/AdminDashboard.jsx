import { SectionHeading } from '../../components/SectionHeading.jsx'

export function AdminDashboard({
  admin,
  loginForm,
  showDemoLoginHint,
  onLoginChange,
  onLogin,
  onLogout,
  form,
  onFormChange,
  onSubmit,
  editingId,
  onCancelEdit,
  menuItems,
  categories,
  onEdit,
  onDelete,
  onToggleAvailability,
  categoryForm,
  onCategoryFormChange,
  onCreateCategory,
  onRenameCategory,
  onReorderCategory,
  onDeleteCategory,
  currentTableLabel,
  guestMenuHref,
  tableLinks,
  statusMessage,
  errorMessage,
  isSubmitting,
}) {
  return (
    <section id="admin-panel" className="panel section-panel">
      <SectionHeading
        eyebrow="Admin Dashboard"
        title={admin ? 'Run the hotel menu with confidence' : 'Staff sign-in only'}
        description={
          admin
            ? 'Update dishes, control availability, and print table QR codes from a workspace reserved for the hotel team.'
            : 'This page is kept away from guest QR links. Sign in to reach the protected workspace for menu and table management.'
        }
        action={
          admin ? (
            <button type="button" className="secondary-button" onClick={onLogout}>
              Logout {admin.name}
            </button>
          ) : (
            <a href={guestMenuHref} className="secondary-button link-button">
              Return to guest menu
            </a>
          )
        }
      />

      {statusMessage ? <p className="status-banner">{statusMessage}</p> : null}
      {errorMessage ? <p className="error-banner">{errorMessage}</p> : null}

      <div className={admin ? 'admin-shell' : 'admin-auth-shell'}>
        {!admin ? (
          <>
            <div className="panel soft-panel admin-auth-card">
              <p className="mini-label">Protected workspace</p>
              <h3>Keep hotel operations private</h3>
              <p>
                Guests only see the dining menu after scanning a table QR. Staff can use this
                separate page to update items, change availability, and prepare printed table codes.
              </p>
              <div className="admin-auth-points">
                <span className="pill-note">Guest QR pages stay public and clean</span>
                <span className="pill-note">Menu edits require a signed-in session</span>
                <span className="pill-note">Each table gets its own downloadable QR</span>
              </div>
            </div>

            <form className="panel soft-panel admin-form admin-login-card" onSubmit={onLogin}>
              <p className="mini-label">Staff login</p>
              <h3>Sign in to open the admin workspace</h3>
              <label>
                Username
                <input name="username" value={loginForm.username} onChange={onLoginChange} required />
              </label>
              <label>
                Password
                <input
                  name="password"
                  type="password"
                  value={loginForm.password}
                  onChange={onLoginChange}
                  required
                />
              </label>
              <button type="submit" className="primary-button" disabled={isSubmitting}>
                Open admin workspace
              </button>
              {showDemoLoginHint ? <span className="pill-note">Demo login: admin / admin123</span> : null}
            </form>
          </>
        ) : (
          <>
            <div className="admin-column">
              <form className="panel soft-panel admin-form" onSubmit={onSubmit}>
                <h3>{editingId ? 'Edit menu item' : 'Add menu item'}</h3>

                <label>
                  Item name
                  <input name="name" value={form.name} onChange={onFormChange} required />
                </label>

                <label>
                  Category
                  <select name="category" value={form.category} onChange={onFormChange} required>
                    {categories.map((category) => (
                      <option key={category.id} value={category.name}>
                        {category.name}
                      </option>
                    ))}
                  </select>
                </label>

                <label>
                  Price
                  <input name="price" type="number" min="0" value={form.price} onChange={onFormChange} required />
                </label>

                <label>
                  Description
                  <textarea name="description" rows="4" value={form.description} onChange={onFormChange} required />
                </label>

                <label>
                  Image URL
                  <input name="image" value={form.image} onChange={onFormChange} placeholder="https://..." />
                </label>

                <div className="check-grid">
                  <label className="switch-row">
                    <input name="available" type="checkbox" checked={form.available} onChange={onFormChange} />
                    <span>Available</span>
                  </label>
                  <label className="switch-row">
                    <input name="spicy" type="checkbox" checked={form.spicy} onChange={onFormChange} />
                    <span>Spicy</span>
                  </label>
                  <label className="switch-row">
                    <input name="featured" type="checkbox" checked={form.featured} onChange={onFormChange} />
                    <span>Featured</span>
                  </label>
                </div>

                <div className="button-row">
                  <button type="submit" className="primary-button" disabled={isSubmitting}>
                    {editingId ? 'Save changes' : 'Create item'}
                  </button>
                  {editingId ? (
                    <button type="button" className="secondary-button" onClick={onCancelEdit}>
                      Cancel
                    </button>
                  ) : null}
                </div>
              </form>

              <div className="panel soft-panel admin-form">
                <h3>Category module</h3>
                <form className="inline-form" onSubmit={onCreateCategory}>
                  <input
                    name="name"
                    value={categoryForm.name}
                    onChange={onCategoryFormChange}
                    placeholder="New category name"
                    required
                  />
                  <button type="submit" className="primary-button" disabled={isSubmitting}>
                    Add
                  </button>
                </form>

                <div className="category-list">
                  {categories.map((category, index) => (
                    <article key={category.id} className="category-item">
                      <div>
                        <strong>{category.name}</strong>
                        <span>Order {category.order}</span>
                      </div>
                      <div className="inline-actions">
                        <button
                          type="button"
                          className="secondary-button"
                          onClick={() => onRenameCategory(category)}
                        >
                          Rename
                        </button>
                        <button
                          type="button"
                          className="secondary-button"
                          onClick={() => onReorderCategory(category.id, index, -1)}
                          disabled={index === 0}
                        >
                          Up
                        </button>
                        <button
                          type="button"
                          className="secondary-button"
                          onClick={() => onReorderCategory(category.id, index, 1)}
                          disabled={index === categories.length - 1}
                        >
                          Down
                        </button>
                        <button
                          type="button"
                          className="danger-button"
                          onClick={() => onDeleteCategory(category)}
                        >
                          Delete
                        </button>
                      </div>
                    </article>
                  ))}
                </div>
              </div>
            </div>

            <div className="admin-column">
              <div className="panel soft-panel admin-list">
                <div className="stack-head">
                  <div>
                    <p className="mini-label">Menu module</p>
                    <h3>Live menu inventory</h3>
                  </div>
                  <span className="pill-note">{menuItems.length} items</span>
                </div>

                {menuItems.map((item) => (
                  <article key={item.id} className="admin-item">
                    <div>
                      <strong>{item.name}</strong>
                      <p>
                        {item.category} · {item.price} ETB · {item.available ? 'Available' : 'Hidden'}
                      </p>
                    </div>
                    <div className="inline-actions">
                      <button type="button" className="secondary-button" onClick={() => onEdit(item)}>
                        Edit
                      </button>
                      <button
                        type="button"
                        className="secondary-button"
                        onClick={() => onToggleAvailability(item)}
                      >
                        {item.available ? 'Disable' : 'Enable'}
                      </button>
                      <button type="button" className="danger-button" onClick={() => onDelete(item.id)}>
                        Delete
                      </button>
                    </div>
                  </article>
                ))}
              </div>

              <div className="panel soft-panel module-card">
                <p className="mini-label">Hotel QR</p>
                <h3>{currentTableLabel} is live</h3>
                <p>The hotel now uses one public QR code that opens the guest menu without exposing staff tools.</p>
              </div>

              <div className="panel soft-panel admin-list">
                <div className="stack-head">
                  <div>
                    <p className="mini-label">Hotel QR kit</p>
                    <h3>Printable guest access code</h3>
                  </div>
                  <span className="pill-note">{tableLinks.length} hotel link</span>
                </div>

                <div className="qr-admin-grid">
                  {tableLinks.map((table) => (
                    <article key={table.id} className="qr-admin-card">
                      <img src={table.qrImageUrl} alt={`${table.label} QR code`} />
                      <div className="qr-admin-copy">
                        <strong>{table.label}</strong>
                        <p>{table.guestUrl}</p>
                      </div>
                      <div className="inline-actions">
                        <a href={table.guestUrl} className="secondary-button link-button" target="_blank" rel="noreferrer">
                          Open menu
                        </a>
                        <a
                          href={table.qrImageUrl}
                          className="primary-button link-button"
                          download={`${table.slug}-qr.svg`}
                        >
                          Download QR
                        </a>
                      </div>
                    </article>
                  ))}
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </section>
  )
}
