import { useState, Suspense, useEffect } from 'react';
import { Plus, MapPin, ExternalLink, Trash2, AlertCircle, Store as StoreIcon, Globe } from 'lucide-react';
import toast from 'react-hot-toast';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { EmptyState } from '@/components/ui/EmptyState';
import { Modal } from '@/components/ui/Modal';
import { Input } from '@/components/ui/Input';
import { ListSkeleton } from '@/components/ui/Skeleton';
import { useStores, useCreateStore, useDeleteStore } from '@/hooks/useStores';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { createStoreSchema } from '@/lib/schemas';
import type { CreateStoreInput } from '@/lib/schemas';

function StoresContent() {
  const { data: stores, error } = useStores();
  const deleteMutation = useDeleteStore();

  const handleDelete = async (id: number, name: string) => {
    if (confirm(`Are you sure you want to delete "${name}"?`)) {
      try {
        await deleteMutation.mutateAsync(id);
        toast.success(`${name} deleted successfully`);
      } catch (error) {
        toast.error('Failed to delete store. Please try again.');
        console.error('Failed to delete store:', error);
      }
    }
  };

  if (error) {
    return (
      <Card>
        <div className="flex items-center gap-3 text-status-required">
          <AlertCircle size={20} />
          <span>Error loading stores. Please try again.</span>
        </div>
      </Card>
    );
  }

  return stores && stores.length > 0 ? (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {stores.map((store, index) => (
        <div key={store.id} className="animate-fadeIn" style={{ animationDelay: `${index * 50}ms` }}>
          <Card className="hover:shadow-lg transition-all duration-300 hover:border-military-olive/40 hover:-translate-y-1">
          {/* Header */}
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-start gap-3 flex-1">
              <div className="rounded-lg bg-military-sand/40 p-2.5">
                <StoreIcon className="text-military-olive" size={20} />
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="text-lg font-bold text-military-navy mb-1 truncate">{store.name}</h3>
                <div className="flex flex-wrap gap-1.5">
                  {store.is_online && (
                    <Badge variant="info" size="sm">
                      <Globe size={10} />
                      Online
                    </Badge>
                  )}
                  {store.is_in_person && (
                    <Badge variant="success" size="sm">
                      <MapPin size={10} />
                      In-Person
                    </Badge>
                  )}
                </div>
              </div>
            </div>
            <Button
              size="sm"
              variant="danger"
              onClick={() => handleDelete(store.id, store.name)}
              disabled={deleteMutation.isPending}
              className="flex-shrink-0"
            >
              <Trash2 size={14} />
            </Button>
          </div>

          {/* Address */}
          {(store.address_line1 || store.city) && (
            <div className="bg-gray-50 rounded-lg p-3 mb-3">
              <div className="flex items-start gap-2">
                <MapPin size={16} className="text-gray-400 mt-0.5 flex-shrink-0" />
                <div className="text-sm text-gray-700 flex-1">
                  {store.address_line1 && <div className="font-medium">{store.address_line1}</div>}
                  {store.address_line2 && <div>{store.address_line2}</div>}
                  {(store.city || store.state) && (
                    <div className="text-gray-600">
                      {store.city}{store.city && store.state ? ', ' : ''}{store.state} {store.zip_code}
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Website Link */}
          {store.url && (
            <a
              href={store.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center justify-center gap-2 w-full px-4 py-2 bg-military-navy/5 hover:bg-military-navy/10 text-military-navy rounded-lg transition-colors text-sm font-medium group"
            >
              <ExternalLink size={14} className="group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
              Visit Website
            </a>
          )}
          </Card>
        </div>
      ))}
    </div>
  ) : (
    <EmptyState
      icon={StoreIcon}
      title="No Stores Added Yet"
      description="Add stores where you can purchase packing list items. Help the community find the best deals!"
      action={{
        label: 'Add Your First Store',
        onClick: () => {
          const event = new CustomEvent('open-store-modal');
          window.dispatchEvent(event);
        },
        icon: Plus,
      }}
    />
  );
}

export function StoreListPage() {
  const createMutation = useCreateStore();
  const [isModalOpen, setIsModalOpen] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<CreateStoreInput>({
    resolver: zodResolver(createStoreSchema),
    defaultValues: {
      is_online: false,
      is_in_person: true,
    },
  });

  // Listen for custom event from EmptyState
  useEffect(() => {
    const handleOpenModal = () => setIsModalOpen(true);
    window.addEventListener('open-store-modal', handleOpenModal);
    return () => window.removeEventListener('open-store-modal', handleOpenModal);
  }, []);

  const onSubmit = async (data: CreateStoreInput) => {
    try {
      await createMutation.mutateAsync(data);
      toast.success(`${data.name} added successfully!`);
      setIsModalOpen(false);
      reset();
    } catch (error) {
      toast.error('Failed to add store. Please try again.');
      console.error('Failed to create store:', error);
    }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-military-dark">Stores</h1>
          <p className="text-gray-600 mt-2">Manage stores where you can purchase packing list items</p>
        </div>
        <Button variant="success" onClick={() => setIsModalOpen(true)}>
          <Plus className="inline mr-2" size={18} />
          Add Store
        </Button>
      </div>

      <Suspense fallback={<ListSkeleton items={6} />}>
        <StoresContent />
      </Suspense>

      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Add New Store"
      >
        <form onSubmit={handleSubmit(onSubmit)}>
          <Input
            label="Store Name *"
            placeholder="e.g., Army Navy Store"
            error={errors.name?.message}
            {...register('name')}
          />

          <Input
            label="Address Line 1"
            placeholder="123 Main Street"
            error={errors.address_line1?.message}
            {...register('address_line1')}
          />

          <Input
            label="Address Line 2"
            placeholder="Suite 100"
            error={errors.address_line2?.message}
            {...register('address_line2')}
          />

          <div className="grid grid-cols-2 gap-4">
            <Input
              label="City"
              placeholder="City"
              error={errors.city?.message}
              {...register('city')}
            />
            <Input
              label="State"
              placeholder="State"
              error={errors.state?.message}
              {...register('state')}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <Input
              label="ZIP Code"
              placeholder="12345"
              error={errors.zip_code?.message}
              {...register('zip_code')}
            />
            <Input
              label="Country"
              placeholder="USA"
              error={errors.country?.message}
              {...register('country')}
            />
          </div>

          <Input
            label="Website URL"
            placeholder="https://example.com"
            error={errors.url?.message}
            {...register('url')}
          />

          <div className="mb-4">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                className="rounded text-military-navy"
                {...register('is_online')}
              />
              <span className="text-sm text-military-dark">Available Online</span>
            </label>
          </div>

          <div className="mb-4">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                className="rounded text-military-navy"
                {...register('is_in_person')}
              />
              <span className="text-sm text-military-dark">Available In-Person</span>
            </label>
          </div>

          <div className="flex gap-4 mt-6">
            <Button
              type="submit"
              variant="success"
              disabled={createMutation.isPending}
            >
              {createMutation.isPending ? 'Adding...' : 'Add Store'}
            </Button>
            <Button
              type="button"
              variant="secondary"
              onClick={() => setIsModalOpen(false)}
            >
              Cancel
            </Button>
          </div>

          {createMutation.isError && (
            <div className="mt-4 p-3 bg-status-required/10 border border-status-required rounded-md">
              <p className="text-sm text-status-required">
                Failed to add store. Please try again.
              </p>
            </div>
          )}
        </form>
      </Modal>
    </div>
  );
}
