import { useEffect, useMemo, useState } from 'react'
import { AdminDashboard } from '../features/admin/AdminDashboard.jsx'
import { GuestMenuSection } from '../features/guest/GuestMenuSection.jsx'
import { QrShowcase } from '../features/qr/QrShowcase.jsx'
import { apiFetch } from '../services/api.js'

const defaultImage =
  'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?auto=format&fit=crop&w=900&q=80'

const emptyForm = {
  name: '',
  category: '',
  price: '',
  description: '',
  image: '',
  available: true,
  spicy: false,
  featured: false,
}

const adminDefaults = import.meta.env.DEV
  ? {
      username: 'admin',
      password: 'admin123',
    }
  : {
      username: '',
      password: '',
    }

function getTableSlug() {
  if (typeof window === 'undefined') {
    return null
  }

  const pathMatch = window.location.pathname.match(/^\/table\/([a-z0-9-]+)$/i)

  if (pathMatch) {
    return pathMatch[1]
  }

  const params = new URLSearchParams(window.location.search)
  return params.get('table')
}

function getRestaurantSlug() {
  if (typeof window === 'undefined') {
    return null
  }

  const pathMatch = window.location.pathname.match(/^\/(?:r|admin)\/([a-z0-9-]+)\/?$/i)
  return pathMatch ? pathMatch[1] : null
}

function isAdminView() {
  if (typeof window === 'undefined') {
    return false
  }

  const { pathname, search } = window.location
  const params = new URLSearchParams(search)

  return /^\/admin(?:\/[a-z0-9-]+)?\/?$/i.test(pathname) || params.get('view') === 'admin'
}

function buildAbsoluteUrl(path) {
  if (typeof window === 'undefined') {
    return path
  }

  return new URL(path, window.location.origin).toString()
}

function formatSlug(slug) {
  if (!slug) {
    return ''
  }

  return slug
    .split('-')
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ')
}

function moveItem(array, index, delta) {
  const nextIndex = index + delta

  if (nextIndex < 0 || nextIndex >= array.length) {
    return array
  }

  const next = [...array]
  const [item] = next.splice(index, 1)
  next.splice(nextIndex, 0, item)
  return next
}

export default function App() {
  const [restaurant, setRestaurant] = useState(null)
  const [menuItems, setMenuItems] = useState([])
  const [categories, setCategories] = useState([])
  const [tables, setTables] = useState([])
  const [activeCategory, setActiveCategory] = useState('All')
  const [showAvailableOnly, setShowAvailableOnly] = useState(false)
  const [admin, setAdmin] = useState(null)
  const [form, setForm] = useState(emptyForm)
  const [categoryForm, setCategoryForm] = useState({ name: '' })
  const [editingId, setEditingId] = useState(null)
  const [loginForm, setLoginForm] = useState(adminDefaults)
  const [statusMessage, setStatusMessage] = useState('')
  const [errorMessage, setErrorMessage] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isUploadingImage, setIsUploadingImage] = useState(false)
  const requestedRestaurantSlug = getRestaurantSlug()

  function restaurantApiPath(path) {
    if (!restaurant?.slug && !requestedRestaurantSlug) {
      return path
    }

    const slug = restaurant?.slug || requestedRestaurantSlug
    const separator = path.includes('?') ? '&' : '?'
    return `${path}${separator}restaurant=${encodeURIComponent(slug)}`
  }

  useEffect(() => {
    async function bootstrap() {
      try {
        const [bootstrapPayload, mePayload] = await Promise.all([
          apiFetch(requestedRestaurantSlug ? `/api/bootstrap?restaurant=${encodeURIComponent(requestedRestaurantSlug)}` : '/api/bootstrap'),
          apiFetch('/api/auth/me').catch(() => null),
        ])

        setRestaurant(bootstrapPayload.restaurant)
        setMenuItems(bootstrapPayload.menuItems)
        setCategories(bootstrapPayload.categories)
        setTables(bootstrapPayload.tables)

        if (bootstrapPayload.categories.length > 0) {
          setForm((current) => ({
            ...current,
            category: bootstrapPayload.categories[0].name,
          }))
        }

        if (mePayload?.admin) {
          setAdmin(mePayload.admin)
        }
      } catch (error) {
        setErrorMessage(error.message)
      } finally {
        setIsLoading(false)
      }
    }

    bootstrap()
  }, [requestedRestaurantSlug])

  useEffect(() => {
    if (typeof document === 'undefined') {
      return
    }

    document.title = restaurant?.name ? `${restaurant.name} QR Menu` : 'Hotel QR Menu'
  }, [restaurant?.name])

  useEffect(() => {
    if (typeof window === 'undefined') {
      return
    }

    const params = new URLSearchParams(window.location.search)
    if (params.get('view') === 'admin' && !/^\/admin(?:\/[a-z0-9-]+)?\/?$/i.test(window.location.pathname)) {
      window.history.replaceState({}, '', requestedRestaurantSlug ? `/admin/${requestedRestaurantSlug}` : '/admin')
    }
  }, [requestedRestaurantSlug])

  const tableSlug = getTableSlug()

  const currentTable = useMemo(() => {
    if (tableSlug) {
      return tables.find((table) => table.slug === tableSlug || String(table.number) === tableSlug)
    }

    return tables[0] || null
  }, [tableSlug, tables])

  const adminView = isAdminView()
  const activeRestaurantSlug = restaurant?.slug || requestedRestaurantSlug || ''
  const fallbackRestaurantName = formatSlug(activeRestaurantSlug) || 'Restaurant'
  const guestMenuHref = activeRestaurantSlug ? `/r/${activeRestaurantSlug}` : currentTable?.path || '/'
  const adminHref = activeRestaurantSlug ? `/admin/${activeRestaurantSlug}` : '/admin'
  const displayTable =
    currentTable ||
    (activeRestaurantSlug
      ? {
          label: `${fallbackRestaurantName} Menu`,
          path: `/r/${activeRestaurantSlug}`,
        }
      : null)
  const currentTableLabel = displayTable?.label || 'Hotel Menu'
  const tableLinks = useMemo(
    () =>
      tables.map((table) => {
        const guestUrl = buildAbsoluteUrl(table.path)
        return {
          ...table,
          guestUrl,
          qrImageUrl: `/api/tables/${table.slug}/qr?target=${encodeURIComponent(guestUrl)}`,
        }
      }),
    [tables],
  )
  const currentTableLink = useMemo(
    () => tableLinks.find((table) => table.slug === currentTable?.slug) || null,
    [currentTable?.slug, tableLinks],
  )

  const featuredItems = useMemo(
    () => menuItems.filter((item) => item.featured).slice(0, 3),
    [menuItems],
  )

  const visibleItems = useMemo(
    () =>
      menuItems.filter((item) => {
        if (activeCategory !== 'All' && item.category !== activeCategory) {
          return false
        }

        if (showAvailableOnly && !item.available) {
          return false
        }

        return true
      }),
    [activeCategory, menuItems, showAvailableOnly],
  )

  function clearMessages() {
    setStatusMessage('')
    setErrorMessage('')
  }

  function resetForm(nextCategories = categories) {
    setEditingId(null)
    setForm({
      ...emptyForm,
      category: nextCategories[0]?.name || '',
    })
  }

  function handleFormChange(event) {
    const { name, value, checked, type } = event.target
    setForm((current) => ({
      ...current,
      [name]: type === 'checkbox' ? checked : value,
    }))
  }

  function handleLoginChange(event) {
    const { name, value } = event.target
    setLoginForm((current) => ({
      ...current,
      [name]: value,
    }))
  }

  async function handleImageUpload(event) {
    const [file] = event.target.files
    if (!file) {
      return
    }

    clearMessages()
    setIsUploadingImage(true)

    const uploadForm = new FormData()
    uploadForm.append('image', file)

    try {
      const response = await apiFetch(restaurantApiPath('/api/menu/images'), {
        method: 'POST',
        body: uploadForm,
      })

      setForm((current) => ({
        ...current,
        image: response.imageUrl,
      }))
      setStatusMessage('Image uploaded. Save the item to use it on the menu.')
    } catch (error) {
      setErrorMessage(error.message)
    } finally {
      setIsUploadingImage(false)
      event.target.value = ''
    }
  }

  function handleCategoryFormChange(event) {
    const { name, value } = event.target
    setCategoryForm((current) => ({
      ...current,
      [name]: value,
    }))
  }

  async function handleLogin(event) {
    event.preventDefault()
    clearMessages()
    setIsSubmitting(true)

    try {
      const payload = await apiFetch('/api/auth/login', {
        method: 'POST',
        body: JSON.stringify({
          ...loginForm,
          restaurantSlug: restaurant?.slug || requestedRestaurantSlug || '',
        }),
      })

      setAdmin(payload.admin)
      setStatusMessage(`Welcome back, ${payload.admin.name}.`)

      if (typeof window !== 'undefined') {
        if (!/^\/admin(?:\/[a-z0-9-]+)?\/?$/i.test(window.location.pathname)) {
          window.location.assign(`${adminHref}#admin-panel`)
          return
        }

        window.location.hash = 'admin-panel'
      }
    } catch (error) {
      setErrorMessage(error.message)
    } finally {
      setIsSubmitting(false)
    }
  }

  async function handleLogout() {
    clearMessages()

    try {
      await apiFetch('/api/auth/logout', { method: 'POST' })
    } catch {
      // Local logout should still succeed if the network request fails.
    }

    setAdmin(null)
    resetForm()
    setStatusMessage('Admin session closed.')
  }

  async function handleSubmit(event) {
    event.preventDefault()
    clearMessages()
    setIsSubmitting(true)

    const payload = {
      ...form,
      price: Number(form.price),
      image: form.image || defaultImage,
    }

    try {
      if (editingId) {
        const response = await apiFetch(restaurantApiPath(`/api/menu/${editingId}`), {
          method: 'PUT',
          body: JSON.stringify({ ...payload, restaurantSlug: restaurant?.slug }),
        })

        setMenuItems((current) =>
          current.map((item) => (item.id === editingId ? response.menuItem : item)),
        )
        setStatusMessage('Menu item updated.')
      } else {
        const response = await apiFetch(restaurantApiPath('/api/menu'), {
          method: 'POST',
          body: JSON.stringify({ ...payload, restaurantSlug: restaurant?.slug }),
        })

        setMenuItems((current) => [response.menuItem, ...current])
        setStatusMessage('Menu item added.')
      }

      resetForm()
    } catch (error) {
      setErrorMessage(error.message)
    } finally {
      setIsSubmitting(false)
    }
  }

  function handleEdit(item) {
    clearMessages()
    setEditingId(item.id)
    setForm({
      name: item.name,
      category: item.category,
      price: String(item.price),
      description: item.description,
      image: item.image,
      available: item.available,
      spicy: item.spicy,
      featured: item.featured,
    })
  }

  async function handleDelete(id) {
    clearMessages()
    setIsSubmitting(true)

    try {
      await apiFetch(restaurantApiPath(`/api/menu/${id}`), { method: 'DELETE' })
      setMenuItems((current) => current.filter((item) => item.id !== id))

      if (editingId === id) {
        resetForm()
      }

      setStatusMessage('Menu item deleted.')
    } catch (error) {
      setErrorMessage(error.message)
    } finally {
      setIsSubmitting(false)
    }
  }

  async function handleToggleAvailability(item) {
    clearMessages()
    setIsSubmitting(true)

    try {
      const response = await apiFetch(restaurantApiPath(`/api/menu/${item.id}`), {
        method: 'PUT',
        body: JSON.stringify({
          ...item,
          restaurantSlug: restaurant?.slug,
          available: !item.available,
        }),
      })

      setMenuItems((current) =>
        current.map((entry) => (entry.id === item.id ? response.menuItem : entry)),
      )
      setStatusMessage('Availability updated.')
    } catch (error) {
      setErrorMessage(error.message)
    } finally {
      setIsSubmitting(false)
    }
  }

  async function handleCreateCategory(event) {
    event.preventDefault()
    clearMessages()
    setIsSubmitting(true)

    try {
      const response = await apiFetch(restaurantApiPath('/api/categories'), {
        method: 'POST',
        body: JSON.stringify({ name: categoryForm.name, restaurantSlug: restaurant?.slug }),
      })

      setCategories(response.categories)
      setCategoryForm({ name: '' })
      setForm((current) => ({
        ...current,
        category: current.category || response.category.name,
      }))
      setStatusMessage('Category added.')
    } catch (error) {
      setErrorMessage(error.message)
    } finally {
      setIsSubmitting(false)
    }
  }

  async function handleRenameCategory(category) {
    const nextName = window.prompt('Rename category', category.name)?.trim()

    if (!nextName || nextName === category.name) {
      return
    }

    clearMessages()
    setIsSubmitting(true)

    try {
      const response = await apiFetch(restaurantApiPath(`/api/categories/${category.id}`), {
        method: 'PUT',
        body: JSON.stringify({ name: nextName, previousName: category.name, restaurantSlug: restaurant?.slug }),
      })

      setCategories(response.categories)
      setMenuItems((current) =>
        current.map((item) =>
          item.category === category.name ? { ...item, category: nextName } : item,
        ),
      )

      setForm((current) => ({
        ...current,
        category: current.category === category.name ? nextName : current.category,
      }))
      setStatusMessage('Category renamed.')
    } catch (error) {
      setErrorMessage(error.message)
    } finally {
      setIsSubmitting(false)
    }
  }

  async function handleReorderCategory(_id, index, delta) {
    const reordered = moveItem(categories, index, delta)

    if (reordered === categories) {
      return
    }

    clearMessages()
    setIsSubmitting(true)

    try {
      const response = await apiFetch(restaurantApiPath('/api/categories/reorder'), {
        method: 'PUT',
        body: JSON.stringify({ categoryIds: reordered.map((item) => item.id), restaurantSlug: restaurant?.slug }),
      })

      setCategories(response.categories)
      setStatusMessage('Category order updated.')
    } catch (error) {
      setErrorMessage(error.message)
    } finally {
      setIsSubmitting(false)
    }
  }

  async function handleDeleteCategory(category) {
    const shouldDelete = window.confirm(
      `Delete "${category.name}"? This only works if no menu items still use it.`,
    )

    if (!shouldDelete) {
      return
    }

    clearMessages()
    setIsSubmitting(true)

    try {
      await apiFetch(restaurantApiPath(`/api/categories/${category.id}`), { method: 'DELETE' })
      const nextCategories = categories.filter((item) => item.id !== category.id)
      setCategories(nextCategories)

      if (form.category === category.name) {
        resetForm(nextCategories)
      }

      setStatusMessage('Category deleted.')
    } catch (error) {
      setErrorMessage(error.message)
    } finally {
      setIsSubmitting(false)
    }
  }

  const heroEyebrow = adminView ? `${restaurant?.name || fallbackRestaurantName} Staff Access` : `Welcome to ${restaurant?.name || fallbackRestaurantName}`
  const heroTitle = adminView ? `${restaurant?.name || fallbackRestaurantName} Admin` : restaurant?.name || `${fallbackRestaurantName} Menu`
  const heroText = adminView
    ? 'Sign in to manage dishes, keep categories organized, and print live QR codes for every table without exposing hotel staff tools to guests.'
    : 'Discover signature dishes, fresh breakfast favorites, and table-side service designed to make every stay at the hotel feel easy, warm, and memorable.'

  if (isLoading) {
    return (
      <main className="page-shell">
        <section className="panel loading-panel">
          <p className="eyebrow">Loading</p>
          <h1>Preparing your hotel menu experience...</h1>
        </section>
      </main>
    )
  }

  return (
    <main className="page-shell">
      <section className="hero-grid">
        <div className="panel hero-copy">
          <p className="eyebrow">{heroEyebrow}</p>
          <h1>{heroTitle}</h1>
          <p className="hero-text">{heroText}</p>

          <div className="hero-actions">
            {adminView ? (
              <>
                <a href={guestMenuHref} className="primary-button link-button">
                  View Guest Menu
                </a>
                <a href="#admin-panel" className="secondary-button link-button">
                  Open Admin Workspace
                </a>
              </>
            ) : (
              <a href="#guest-menu" className="primary-button link-button">
                Preview Guest Menu
              </a>
            )}
          </div>

          <div className="stats-grid">
            <article>
              <strong>{menuItems.length}</strong>
              <span>menu items</span>
            </article>
            <article>
              <strong>{categories.length}</strong>
              <span>categories</span>
            </article>
            <article>
              <strong>{tableLinks.length}</strong>
              <span>hotel QR code</span>
            </article>
          </div>

          <div className="module-grid">
            <article className="module-card">
              <p className="mini-label">Hotel dining</p>
              <h3>Breakfast, mains, desserts, and drinks</h3>
              <p>
                From early coffee to late-evening comfort dishes, guests can explore a menu shaped
                around the hotel&apos;s most loved flavors.
              </p>
            </article>
            <article className="module-card">
              <p className="mini-label">Guest experience</p>
              <h3>One hotel QR, clear choices, and smooth ordering</h3>
              <p>
                One hotel QR opens a simple menu view so guests can browse availability, choose with
                confidence, and enjoy a polished hotel experience.
              </p>
            </article>
          </div>
        </div>

        <section className="panel hero-visual">
          <QrShowcase
            table={displayTable}
            featuredItems={featuredItems}
            qrImageUrl={currentTableLink?.qrImageUrl}
          />
        </section>
      </section>

      {!adminView ? (
        <GuestMenuSection
          categories={categories}
          activeCategory={activeCategory}
          setActiveCategory={setActiveCategory}
          showAvailableOnly={showAvailableOnly}
          setShowAvailableOnly={setShowAvailableOnly}
          visibleItems={visibleItems}
          restaurant={restaurant}
          currentTableLabel={currentTableLabel}
          statusMessage={statusMessage}
          errorMessage={errorMessage}
        />
      ) : (
        <AdminDashboard
          admin={admin}
          loginForm={loginForm}
          showDemoLoginHint={import.meta.env.DEV}
          onLoginChange={handleLoginChange}
          onLogin={handleLogin}
          onLogout={handleLogout}
          form={form}
          onFormChange={handleFormChange}
          onImageUpload={handleImageUpload}
          onSubmit={handleSubmit}
          editingId={editingId}
          onCancelEdit={() => resetForm()}
          menuItems={menuItems}
          categories={categories}
          onEdit={handleEdit}
          onDelete={handleDelete}
          onToggleAvailability={handleToggleAvailability}
          categoryForm={categoryForm}
          onCategoryFormChange={handleCategoryFormChange}
          onCreateCategory={handleCreateCategory}
          onRenameCategory={handleRenameCategory}
          onReorderCategory={handleReorderCategory}
          onDeleteCategory={handleDeleteCategory}
          currentTableLabel={currentTableLabel}
          guestMenuHref={guestMenuHref}
          tableLinks={tableLinks}
          statusMessage={statusMessage}
          errorMessage={errorMessage}
          isSubmitting={isSubmitting}
          isUploadingImage={isUploadingImage}
        />
      )}
    </main>
  )
}
