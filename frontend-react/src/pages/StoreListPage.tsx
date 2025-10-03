import { useState } from 'react';
import { Plus, MapPin, ExternalLink, Trash2 } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Modal } from '@/components/ui/Modal';
import { Input } from '@/components/ui/Input';
import { useStores, useCreateStore, useDeleteStore } from '@/hooks/useStores';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { createStoreSchema } from '@/lib/schemas';
import type { CreateStoreInput } from '@/lib/schemas';

export function StoreListPage() {
  const { data: stores, isLoading, error } = useStores();
  const createMutation = useCreateStore();
  const deleteMutation = useDeleteStore();
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

  const onSubmit = async (data: CreateStoreInput) => {
    try {
      await createMutation.mutateAsync(data);
      setIsModalOpen(false);
      reset();
    } catch (error) {
      console.error('Failed to create store:', error);
    }
  };

  const handleDelete = async (id: number) => {
    if (confirm('Are you sure you want to delete this store?')) {
      try {
        await deleteMutation.mutateAsync(id);
      } catch (error) {
        console.error('Failed to delete store:', error);
      }
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <div className="text-lg text-military-dark">Loading stores...</div>
      </div>
    );
  }

  if (error) {
    return (
      <Card>
        <div className="text-status-required">Error loading stores. Please try again.</div>
      </Card>
    );
  }

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

      {stores && stores.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {stores.map((store) => (
            <Card key={store.id}>
              <div className="flex items-start justify-between mb-3">
                <h3 className="text-xl font-semibold text-military-navy">{store.name}</h3>
                <Button
                  size="sm"
                  variant="danger"
                  onClick={() => handleDelete(store.id)}
                  disabled={deleteMutation.isPending}
                >
                  <Trash2 size={16} />
                </Button>
              </div>

              <div className="space-y-2 text-sm">
                {(store.address_line1 || store.city) && (
                  <div className="flex items-start gap-2">
                    <MapPin size={16} className="text-gray-500 mt-0.5 flex-shrink-0" />
                    <div className="text-gray-600">
                      {store.address_line1 && <div>{store.address_line1}</div>}
                      {store.address_line2 && <div>{store.address_line2}</div>}
                      {(store.city || store.state) && (
                        <div>
                          {store.city}{store.city && store.state ? ', ' : ''}{store.state} {store.zip_code}
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {store.url && (
                  <div className="flex items-center gap-2">
                    <ExternalLink size={16} className="text-gray-500" />
                    <a
                      href={store.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-military-navy hover:underline truncate"
                    >
                      Visit Website
                    </a>
                  </div>
                )}

                <div className="flex flex-wrap gap-2 mt-3">
                  {store.is_online && (
                    <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs">
                      Online
                    </span>
                  )}
                  {store.is_in_person && (
                    <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs">
                      In-Person
                    </span>
                  )}
                </div>
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <p className="text-gray-600 text-center py-8">
            No stores found. Add your first store to get started!
          </p>
        </Card>
      )}

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
