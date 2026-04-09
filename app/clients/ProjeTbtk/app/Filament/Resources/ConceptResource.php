<?php

namespace App\Filament\Resources;

use App\Filament\Resources\ConceptResource\Pages;
use App\Models\Concept;
use App\Models\Topic;
use Filament\Forms;
use Filament\Forms\Form;
use Filament\Resources\Resource;
use Filament\Tables;
use Filament\Tables\Table;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\SoftDeletingScope;

class ConceptResource extends Resource
{
    protected static ?string $model = Concept::class;

    protected static ?string $navigationIcon = 'heroicon-o-rectangle-stack';
    protected static ?string $navigationLabel = 'Kavram Bankasi';
    protected static ?string $modelLabel = 'Kavram';
    protected static ?string $pluralModelLabel = 'Kavram Bankasi';
    protected static ?string $navigationGroup = 'Ileri Seviye';

    public static function shouldRegisterNavigation(): bool
    {
        return false;
    }

    public static function form(Form $form): Form
    {
        return $form
            ->schema([
                Forms\Components\Select::make('topic_id')
                    ->label('Konu')
                    ->options(
                        Topic::query()
                            ->with('unit')
                            ->orderBy('unit_id')
                            ->orderBy('topic_no')
                            ->get()
                            ->mapWithKeys(fn (Topic $topic) => [
                                $topic->id => ($topic->unit?->grade ?? '?') . '. Sinif / U' . ($topic->unit?->unit_no ?? '?') . ' / K' . $topic->topic_no . ' - ' . $topic->name,
                            ])
                            ->all()
                    )
                    ->searchable()
                    ->required()
                    ->native(false),
                Forms\Components\TextInput::make('name')
                    ->label('Kavram Adi')
                    ->required(),
                Forms\Components\Textarea::make('definition')
                    ->label('Tanim')
                    ->columnSpanFull(),
                Forms\Components\TextInput::make('order')
                    ->label('Liste Sirasi')
                    ->required()
                    ->numeric()
                    ->default(0),
            ]);
    }

    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                Tables\Columns\TextColumn::make('topic.name')
                    ->label('Konu')
                    ->searchable(),
                Tables\Columns\TextColumn::make('name')
                    ->label('Kavram')
                    ->searchable(),
                Tables\Columns\TextColumn::make('order')
                    ->label('Sira')
                    ->numeric()
                    ->sortable(),
                Tables\Columns\TextColumn::make('created_at')
                    ->dateTime()
                    ->sortable()
                    ->toggleable(isToggledHiddenByDefault: true),
                Tables\Columns\TextColumn::make('updated_at')
                    ->dateTime()
                    ->sortable()
                    ->toggleable(isToggledHiddenByDefault: true),
            ])
            ->filters([
                Tables\Filters\TrashedFilter::make(),
            ])
            ->actions([
                Tables\Actions\ViewAction::make(),
                Tables\Actions\EditAction::make(),
            ])
            ->bulkActions([
                Tables\Actions\BulkActionGroup::make([
                    Tables\Actions\DeleteBulkAction::make(),
                    Tables\Actions\ForceDeleteBulkAction::make(),
                    Tables\Actions\RestoreBulkAction::make(),
                ]),
            ]);
    }

    public static function getRelations(): array
    {
        return [
            //
        ];
    }

    public static function getPages(): array
    {
        return [
            'index' => Pages\ListConcepts::route('/'),
            'create' => Pages\CreateConcept::route('/create'),
            'view' => Pages\ViewConcept::route('/{record}'),
            'edit' => Pages\EditConcept::route('/{record}/edit'),
        ];
    }

    public static function getEloquentQuery(): Builder
    {
        return parent::getEloquentQuery()
            ->withoutGlobalScopes([
                SoftDeletingScope::class,
            ]);
    }
}
