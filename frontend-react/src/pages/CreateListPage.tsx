import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import { useCreatePackingList } from '@/hooks/usePackingListMutations';
import { createPackingListSchema } from '@/lib/schemas';
import type { CreatePackingListInput } from '@/lib/schemas';

const PACKING_LIST_TYPES = [
  { value: 'course', label: 'Course' },
  { value: 'selection', label: 'Selection' },
  { value: 'training', label: 'Training' },
  { value: 'deployment', label: 'Deployment' },
  { value: 'other', label: 'Other' },
];

export function CreateListPage() {
  const navigate = useNavigate();
  const createMutation = useCreatePackingList();

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<CreatePackingListInput>({
    resolver: zodResolver(createPackingListSchema),
    defaultValues: {
      type: 'course',
    },
  });

  const selectedType = watch('type');

  const onSubmit = async (data: CreatePackingListInput) => {
    try {
      const result = await createMutation.mutateAsync(data);
      navigate(`/list/${result.data.id}`);
    } catch (error) {
      console.error('Failed to create packing list:', error);
    }
  };

  return (
    <div>
      <div className="mb-6">
        <Button
          variant="secondary"
          onClick={() => navigate('/')}
          className="mb-4"
        >
          <ArrowLeft className="inline mr-2" size={16} />
          Back to Lists
        </Button>
        <h1 className="text-3xl font-bold text-military-dark">Create New Packing List</h1>
      </div>

      <Card>
        <form onSubmit={handleSubmit(onSubmit)}>
          <Input
            label="List Name *"
            placeholder="e.g., Ranger School Packing List"
            error={errors.name?.message}
            {...register('name')}
          />

          <div className="mb-4">
            <label className="block text-sm font-medium text-military-dark mb-1">
              Description
            </label>
            <textarea
              placeholder="Optional description of this packing list"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-military-navy focus:border-transparent transition-colors duration-200"
              rows={4}
              {...register('description')}
            />
            {errors.description && (
              <p className="mt-1 text-sm text-status-required">{errors.description.message}</p>
            )}
          </div>

          <Select
            label="List Type *"
            options={PACKING_LIST_TYPES}
            error={errors.type?.message}
            {...register('type')}
          />

          {selectedType === 'other' && (
            <Input
              label="Custom Type"
              placeholder="Specify custom type"
              error={errors.custom_type?.message}
              {...register('custom_type')}
            />
          )}

          <div className="flex gap-4 mt-6">
            <Button
              type="submit"
              variant="success"
              disabled={createMutation.isPending}
            >
              {createMutation.isPending ? 'Creating...' : 'Create List'}
            </Button>
            <Button
              type="button"
              variant="secondary"
              onClick={() => navigate('/')}
            >
              Cancel
            </Button>
          </div>

          {createMutation.isError && (
            <div className="mt-4 p-3 bg-status-required/10 border border-status-required rounded-md">
              <p className="text-sm text-status-required">
                Failed to create packing list. Please try again.
              </p>
            </div>
          )}
        </form>
      </Card>
    </div>
  );
}
